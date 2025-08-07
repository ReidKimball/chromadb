# Backend deploy

cd backend

docker build -t chromadb-backend .

docker tag chromadb-backend "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-backend:latest"

docker push "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-backend:latest"

gcloud run deploy chromadb-backend --image "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-backend:latest" --region us-central1 --allow-unauthenticated --project=reidkimball-website

# Frontend deploy

cd frontend

docker build --no-cache --build-arg NEXT_PUBLIC_API_URL=https://chromadb-backend-165871915889.us-central1.run.app -t chromadb-app .

docker tag chromadb-app "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-app:latest"

docker push "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-app:latest"

gcloud run deploy chromadb-app --image "us-central1-docker.pkg.dev/reidkimball-website/chromadb-repo/chromadb-app:latest" --region us-central1 --allow-unauthenticated --set-env-vars=NEXT_PUBLIC_API_URL=https://chromadb-backend-165871915889.us-central1.run.app --project=reidkimball-website

