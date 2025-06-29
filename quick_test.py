import os
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials, APIClient

load_dotenv(dotenv_path=Path(__file__).with_name('.env'))

creds = Credentials(
    api_key = os.getenv("WX_API_KEY"),
    url     = "https://us-south.ml.cloud.ibm.com"
)

client = APIClient(credentials=creds, project_id=os.getenv("WX_PROJECT_ID"))

models = client.foundation_models.get_model_specs()
print("✓ Granite reachable —", len(models["resources"]), "models visible")
