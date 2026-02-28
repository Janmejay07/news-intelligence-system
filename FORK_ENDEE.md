# Fork Endee for This Project

This project uses [Endee](https://github.com/endee-io/endee) as the vector database. To use your forked version:

## 1. Fork on GitHub

1. Go to https://github.com/endee-io/endee
2. Click **Fork** (top right)
3. Fork to your account: `https://github.com/Janmejay07/endee`

## 2. Use Your Fork (Optional)

This project uses the official Endee Docker image by default. To build from your fork:

### Option A: Build Docker image from your fork

```bash
git clone https://github.com/Janmejay07/endee.git
cd endee
docker build --build-arg BUILD_ARCH=avx2 -t endee-custom -f ./infra/Dockerfile .
```

Then update `docker-compose.yml`:

```yaml
services:
  endee:
    image: endee-custom  # Use your built image
    # ... rest unchanged
```

### Option B: Add as Git submodule

```bash
git submodule add https://github.com/Janmejay07/endee.git endee
```

## 3. Default Setup

By default, `docker-compose.yml` uses `endeeio/endee-server:latest` from Docker Hub. No fork is required for standard usage.
