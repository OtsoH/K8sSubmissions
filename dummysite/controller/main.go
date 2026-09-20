package main

import (
	"context"
	"fmt"
	"os"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/util/intstr"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	"k8s.io/utils/ptr"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
	gatewayv1 "sigs.k8s.io/gateway-api/apis/v1"
)

var dummySiteGVK = schema.GroupVersionKind{Group: "dwk.io", Version: "v1", Kind: "DummySite"}

type reconciler struct {
	client.Client
	scheme  *runtime.Scheme
	image   string
	gateway string
}

func (r *reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)

	site := &unstructured.Unstructured{}
	site.SetGroupVersionKind(dummySiteGVK)
	if err := r.Get(ctx, req.NamespacedName, site); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	url, found, err := unstructured.NestedString(site.Object, "spec", "website_url")
	if err != nil || !found || url == "" {
		log.Info("no usable spec.website_url, skipping")
		return ctrl.Result{}, nil
	}

	name := site.GetName()
	labels := map[string]string{"dummysite": name}
	objectMeta := func() metav1.ObjectMeta {
		return metav1.ObjectMeta{Name: name, Namespace: site.GetNamespace()}
	}

	deployment := &appsv1.Deployment{ObjectMeta: objectMeta()}
	if _, err := controllerutil.CreateOrUpdate(ctx, r.Client, deployment, func() error {
		deployment.Spec.Selector = &metav1.LabelSelector{MatchLabels: labels}
		deployment.Spec.Template.Labels = labels
		deployment.Spec.Template.Spec.Containers = []corev1.Container{{
			Name:  "site",
			Image: r.image,
			Ports: []corev1.ContainerPort{{ContainerPort: 3000}},
			Env: []corev1.EnvVar{
				{Name: "WEBSITE_URL", Value: url},
				{Name: "PORT", Value: "3000"},
			},
			ReadinessProbe: &corev1.Probe{ProbeHandler: corev1.ProbeHandler{
				HTTPGet: &corev1.HTTPGetAction{Path: "/healthz", Port: intstr.FromInt32(3000)},
			}},
		}}
		return controllerutil.SetControllerReference(site, deployment, r.scheme)
	}); err != nil {
		return ctrl.Result{}, fmt.Errorf("deployment: %w", err)
	}

	service := &corev1.Service{ObjectMeta: objectMeta()}
	if _, err := controllerutil.CreateOrUpdate(ctx, r.Client, service, func() error {
		service.Spec.Selector = labels
		service.Spec.Ports = []corev1.ServicePort{{Port: 80, TargetPort: intstr.FromInt32(3000)}}
		return controllerutil.SetControllerReference(site, service, r.scheme)
	}); err != nil {
		return ctrl.Result{}, fmt.Errorf("service: %w", err)
	}

	route := &gatewayv1.HTTPRoute{ObjectMeta: objectMeta()}
	if _, err := controllerutil.CreateOrUpdate(ctx, r.Client, route, func() error {
		route.Spec.ParentRefs = []gatewayv1.ParentReference{{Name: gatewayv1.ObjectName(r.gateway)}}
		route.Spec.Rules = []gatewayv1.HTTPRouteRule{{
			Matches: []gatewayv1.HTTPRouteMatch{{Path: &gatewayv1.HTTPPathMatch{
				Type:  ptr.To(gatewayv1.PathMatchPathPrefix),
				Value: ptr.To("/" + name),
			}}},
			Filters: []gatewayv1.HTTPRouteFilter{{
				Type: gatewayv1.HTTPRouteFilterURLRewrite,
				URLRewrite: &gatewayv1.HTTPURLRewriteFilter{Path: &gatewayv1.HTTPPathModifier{
					Type:               gatewayv1.PrefixMatchHTTPPathModifier,
					ReplacePrefixMatch: ptr.To("/"),
				}},
			}},
			BackendRefs: []gatewayv1.HTTPBackendRef{{BackendRef: gatewayv1.BackendRef{
				BackendObjectReference: gatewayv1.BackendObjectReference{
					Name: gatewayv1.ObjectName(name),
					Port: ptr.To(gatewayv1.PortNumber(80)),
				},
			}}},
		}}
		return controllerutil.SetControllerReference(site, route, r.scheme)
	}); err != nil {
		return ctrl.Result{}, fmt.Errorf("httproute: %w", err)
	}

	log.Info("reconciled", "website_url", url, "path", "/"+name)
	return ctrl.Result{}, nil
}

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func main() {
	ctrl.SetLogger(zap.New())

	scheme := runtime.NewScheme()
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(gatewayv1.Install(scheme))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{Scheme: scheme})
	if err != nil {
		ctrl.Log.Error(err, "unable to start manager")
		os.Exit(1)
	}

	site := &unstructured.Unstructured{}
	site.SetGroupVersionKind(dummySiteGVK)

	if err := ctrl.NewControllerManagedBy(mgr).
		For(site).
		Owns(&appsv1.Deployment{}).
		Owns(&corev1.Service{}).
		Owns(&gatewayv1.HTTPRoute{}).
		Complete(&reconciler{
			Client:  mgr.GetClient(),
			scheme:  mgr.GetScheme(),
			image:   env("SITE_IMAGE", "dummysite-site:1.0"),
			gateway: env("GATEWAY_NAME", "dummysite-gateway"),
		}); err != nil {
		ctrl.Log.Error(err, "unable to create controller")
		os.Exit(1)
	}

	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		ctrl.Log.Error(err, "manager exited")
		os.Exit(1)
	}
}
