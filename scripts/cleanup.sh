#!/bin/bash

# Distributed KV Store - Cleanup Script
# Stops all containers (compose and manual) and cleans up resources

set -e  # Exit on any error

echo "🧹 Starting cleanup process..."

# Stop all containers (compose and manual)
echo "📦 Stopping docker-compose services..."
docker-compose down 2>/dev/null || echo "⚠️  No docker-compose services found"

# Stop and remove any manual containers that match our naming pattern
echo "🛑 Stopping manual containers..."
MANUAL_CONTAINERS=$(docker ps -a --filter "name=kv-node-*" --format "{{.Names}}" 2>/dev/null || true)
if [ ! -z "$MANUAL_CONTAINERS" ]; then
    echo "Found manual containers: $MANUAL_CONTAINERS"
    docker stop $MANUAL_CONTAINERS 2>/dev/null || true
    docker rm $MANUAL_CONTAINERS 2>/dev/null || true
else
    echo "No manual containers found"
fi

echo "🧼 Removing unused Docker resources..."
docker system prune -a --volumes -f

# Clean up networks
echo "🌐 Cleaning up networks..."
docker network prune -f

# Optional: Clean up unused images and volumes
echo "🗑️  Cleaning up unused Docker resources..."
docker system prune -f

echo "✅ Cleanup completed successfully!"