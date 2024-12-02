from fastapi import FastAPI
import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from api.routes import get_all_routes
from api.routes.auth import get_auth_routes
from api.routes.dependencies import get_session
from middleware.auth import AuthenticationMiddleware
import os

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Cassandra authentication
username = os.environ.get('CASSANDRA_USERNAME', 'test')  # Replace with your username
password = os.environ.get('CASSANDRA_PASSWORD', 'test')  # Replace with your password
auth_provider = PlainTextAuthProvider(username=username, password=password)

# Connect to Cassandra cluster and keyspace 'grid'
cluster = Cluster(['192.168.178.2'], auth_provider=auth_provider, protocol_version=5)  # Replace with your contact points
session = cluster.connect('grid')

logger.info("Connected to Cassandra keyspace 'grid'")

# Provide session dependency
def get_session_override():
    return session

app.dependency_overrides[get_session] = get_session_override

# Include authentication routes
app.include_router(get_auth_routes(session), prefix="/api/v1", tags=["auth"])

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware, session=session)

# Include other routes
app.include_router(get_all_routes(session), prefix="/api/v1")

# Run the app
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
