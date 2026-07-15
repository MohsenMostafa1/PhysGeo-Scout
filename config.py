"""
Configuration for Mohsen's AI Research & Vacancy Agent System.
All API keys are loaded from .env file. Free APIs that need no key work out of the box.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys (set in .env) ───────────────────────────────────────────────────
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MohsenResearchAgent/1.0")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ─── Profile-Based Search Queries (derived from resume) ──────────────────────
ACADEMIC_QUERIES = {
    "physical_ai": [
        "physical AI embodied intelligence",
        "world models Yann LeCun JEPA",
        "geometric deep learning manifolds",
        "Bayesian deep learning uncertainty quantification",
        "physics-informed neural networks PDE",
        "safe AI robotics embodied prediction",
        "latent predictive architectures JEPA",
        "curvature-aware optimization scientific ML",
        "RGB-D representation learning geometric priors",
        "cognitive architectures video understanding",
    ],
    "robotics": [
        "robotics foundation models",
        "LeRobot Hugging Face robotics",
        "humanoid robot safety AI",
        "sim-to-real transfer robotics",
        "manipulation planning robotics 2025 2026",
        "robot learning from demonstration",
        "adaptive world models robotics",
    ],
    "computer_vision_academic": [
        "3D point cloud segmentation deep learning",
        "multi-view geometry neural networks",
        "image matching challenge 2025",
        "self-supervised visual representation learning",
        "Gaussian constrained representations",
    ],
    "key_labs": [
        "FAIR Meta AI research Yann LeCun",
        "AIM Lab NYU robotics",
        "NYU Courant computer vision",
        "DeepMind robotics research",
        "MIT CSAIL robotics AI",
        "Stanford Vision Lab",
        "ETH Zurich robotics",
        "CMU Robotics Institute",
    ],
}

INDUSTRIAL_QUERIES = {
    "llms": [
        "LLM optimization techniques 2025 2026",
        "large language model fine-tuning LoRA QLoRA",
        "LLM inference optimization TensorRT vLLM",
        "mixture of experts LLM MoE",
        "LLM agents tool use reasoning",
        "context window extension techniques",
        "LLM evaluation benchmarks",
    ],
    "agentic_ai": [
        "Agentic AI frameworks 2025 2026",
        "AI agents multi-agent systems CrewAI LangGraph",
        "tool-augmented LLM agents",
        "autonomous AI agents production",
        "agent memory systems RAG",
        "Google ADK agent development kit",
        "agent orchestration patterns",
    ],
    "computer_vision_industrial": [
        "computer vision edge deployment YOLO",
        "real-time object detection optimization",
        "3D vision LiDAR point cloud industrial",
        "multimodal AI vision language models",
        "Mask2Former image segmentation",
        "vision transformers ViT industrial",
    ],
    "mlops": [
        "MLOps best practices 2025 2026",
        "Kubernetes ML model serving KServe",
        "MLflow experiment tracking production",
        "real-time ML inference pipeline Kafka",
        "distributed training large models",
        "model monitoring drift detection",
        "AI infrastructure GPU optimization",
    ],
    "nvidia": [
        "NVIDIA AI frameworks 2025 2026",
        "TensorRT optimization guide",
        "NVIDIA Triton inference server",
        "CUDA programming optimization",
        "NVIDIA NIM inference microservices",
        "NVIDIA GPU orchestration MIG",
    ],
    "fine_tuning": [
        "fine-tuning techniques 2025 2026",
        "parameter-efficient fine-tuning PEFT",
        "instruction tuning LLM",
        "RLHF DPO alignment techniques",
        "multi-task fine-tuning",
        "fine-tuning on consumer GPUs",
    ],
}

VACANCY_QUERIES = {
    "roles": [
        "AI Research Engineer",
        "Computer Vision Researcher",
        "AI Team Lead",
        "ML Infrastructure Engineer",
        "Applied Scientist AI",
        "Robotics AI Engineer",
        "LLM Engineer",
        "MLOps Engineer",
        "Senior AI Developer",
        "Research Scientist Physical AI",
    ],
    "keywords": [
        "remote", "PyTorch", "computer vision", "LLM",
        "agentic AI", "MLOps", "research", "deep learning",
        "robotics", "physical AI",
    ],
    "sources": [
        "Reddit r/MachineLearning jobs",
        "Reddit r/ArtificialIntelligence jobs",
        "Reddit r/cvjobs",
        "Hacker News Who is Hiring",
        "GitHub jobs board",
        "AI job aggregators",
    ],
}

# ─── Subreddits & Channels to Monitor ────────────────────────────────────────
SUBREDDITS_TO_MONITOR = [
    "MachineLearning", "deeplearning", "ArtificialIntelligence",
    "ComputerVision", "robotics", "MLOps", "LocalLLaMA",
    "LLMDevs", "AgenticAI", "LanguageTechnology", "PyTorch",
    "OpenAI", "nyu", "YannLeCun", "WorldModels", "ResearchPapers",
]

DISCORD_SERVERS = ["Hugging Face", "LAION", "EleutherAI", "MLOps Community"]

HACKER_NEWS_TOPICS = [
    "LLM", "AI agent", "computer vision", "robotics",
    "fine-tuning", "MLOps", "NVIDIA", "Yann LeCun",
    "world model", "agentic",
]

# ─── Schedule ──────────────────────────────────────────────────────────────────
DEFAULT_SCHEDULE_HOURS = 6
MAX_RESULTS_PER_SOURCE = 20
MAX_TOTAL_RESULTS = 100

# ─── Output ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)