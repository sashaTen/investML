gcloud artifacts repositories create retrain `
--repository-format=docker `
--location=asia-northeast3 `
--description="Docker for re-train"

gcloud builds submit `
--tag asia-northeast3-docker.pkg.dev/investml-484904/retrain/retrain:latest

gcloud config set run/region asia-northeast3

gcloud run jobs create my-data-transformation `
--image=asia-northeast3-docker.pkg.dev/investml-484904/retrain/retrain:latest `
--memory=4Gi `
--cpu=2

gcloud run jobs execute my-data-transformation `
--region asia-northeast3