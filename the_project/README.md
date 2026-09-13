The course project started in 1.2: Todoapp written in Python, using uv for dependency management and FASTAPI as the web framework

Since 4.8 it is built by GitHub Actions and deployed by Argo CD, so the image tags in the overlay
kustomizations are written by the pipeline and not by hand. Since 4.9 manifests/ is a Kustomize
base with a production and a staging overlay: a push to main releases staging, a tag releases
production.
