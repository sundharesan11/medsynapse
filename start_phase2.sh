#!/bin/bash

# Quick start script for Phase 2 testing

echo "🧠 MedSynapse Phase 2 - Starting Qdrant and Running Tests"
echo "============================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Start Qdrant
echo ""
echo "🚀 Starting Qdrant..."
docker-compose up -d qdrant

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to start..."
sleep 5

# Check Qdrant health
for i in {1..10}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✅ Qdrant is ready!"
        break
    fi
    echo "   Still waiting... ($i/10)"
    sleep 2
done

# Check if Qdrant is responsive
if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "❌ Qdrant failed to start. Check logs:"
    echo "   docker logs medsynapse-qdrant"
    exit 1
fi

# Run Phase 2 tests
echo ""
echo "🧪 Running Phase 2 tests..."
echo ""
cd backend
python3 tests/test_qdrant.py

echo ""
echo "============================================================"
echo "🎉 Phase 2 testing complete!"
echo ""
echo "📊 Qdrant UI: http://localhost:3001"
echo "📊 Qdrant API: http://localhost:6333"
echo ""
echo "To stop Qdrant:"
echo "  docker-compose down"
