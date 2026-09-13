The course project started in 1.2: Todoapp written in Python, using uv for dependency management and FASTAPI as the web framework

Since 4.8 it is built by .github/workflows/project.yaml and deployed by Argo CD, so the image tags
in manifests/kustomization.yaml are written by the pipeline and not by hand.
