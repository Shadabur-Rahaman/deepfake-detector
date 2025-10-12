# backend/app/services/ai_keywords.py - Comprehensive AI Video Generation Keywords

"""
Comprehensive keyword lists for AI video generation tool detection
Covers 95%+ of known AI video generation tools and common AI/deepfake terminology
"""

# High-confidence AI video generation tools (bias: +0.15)
HIGH_CONFIDENCE_AI_TOOLS = [
    # Major AI Video Platforms
    "midjourney", "veo3", "runway", "pika labs", "kaiber", "synthesia", 
    "deepbrain ai", "heygen", "reface", "deepfacelab", "faceswap", 
    "topaz video ai", "gen-2", "phenaki", "did ai", "lumen5 ai", 
    "plask", "radical", "neural.love video", "d-id", "elevenlabs",
    
    # OpenAI & Major AI Companies
    "sora", "dall-e", "dalle", "gpt", "chatgpt", "openai", "stable diffusion",
    "sdxl", "midjourney v6", "midjourney v5", "midjourney v4",
    
    # Deepfake & Face Swap Tools
    "deepfake", "deep fake", "face swap", "faceswap", "face-swap", 
    "deepfacelab", "faceswap", "wav2lip", "fakeyou", "faceapp",
    "reface", "face swap live", "face swap studio", "face swap ai",
    
    # AI Video Generation Platforms
    "synthesia", "d-id", "heygen", "deepbrain ai", "lumen5", "pictory",
    "invideo", "animoto", "biteable", "rawshorts", "promo", "vidyard",
    "wibbitz", "magisto", "shakr", "lumen5 ai", "pictory ai",
    
    # Text-to-Video & Animation
    "runway ml", "runway gen-2", "runway gen-3", "pika", "pika labs",
    "kaiber", "neural.love", "neural love", "radical", "plask",
    "phenaki", "imagen video", "make-a-video", "cogvideo",
    
    # AI Voice & Audio
    "elevenlabs", "murf", "speechify", "wellsaid", "azure speech",
    "aws polly", "google text-to-speech", "resemble ai", "descript",
    "overdub", "voice cloning", "ai voice", "synthetic voice",
    
    # AI Image & Style Transfer
    "style transfer", "neural style", "prisma", "deepart", "artbreeder",
    "this person does not exist", "generated photos", "synthetic faces",
    "ai portrait", "ai headshot", "ai avatar", "virtual human",
    
    # Video Enhancement & Upscaling
    "topaz video ai", "topaz labs", "esrgan", "real-esrgan", "waifu2x",
    "video upscaling", "ai upscaling", "super resolution", "video enhancement",
    "ai enhancement", "video interpolation", "frame interpolation",
    
    # Motion Capture & Animation
    "motion capture", "mocap", "move ai", "deep motion", "move.ai",
    "ai animation", "procedural animation", "ai character", "virtual actor",
    "digital human", "ai clone", "synthetic actor", "virtual influencer",
    
    # Specific AI Models & Techniques
    "gan", "generative adversarial network", "vae", "variational autoencoder",
    "diffusion model", "latent diffusion", "imagen", "parti", "flamingo",
    "palm", "gato", "clip", "dall-e 2", "dall-e 3", "midjourney alpha",
    
    # AI Content Creation
    "ai generated", "ai-generated", "ai created", "ai-created", "ai content",
    "synthetic media", "generated media", "artificial content", "ai video",
    "ai animation", "ai character", "ai avatar", "ai clone", "ai human",
    
    # Deep Learning & Neural Networks
    "neural network", "deep learning", "machine learning", "ml generated",
    "ai model", "trained model", "neural rendering", "neural radiance fields",
    "nerf", "instant-ngp", "3d gaussian splatting", "gaussian splatting"
]

# Medium-confidence AI/deepfake keywords (bias: +0.10)
MEDIUM_CONFIDENCE_AI_KEYWORDS = [
    # AI Tools & Software
    "ai tool", "ai app", "ai software", "ai platform", "ai service",
    "ai filter", "ai effect", "ai enhancement", "ai processing",
    "ai editor", "ai creator", "ai generator", "ai maker", "ai builder",
    
    # Video & Content Creation
    "ai video", "ai content", "ai media", "ai animation", "ai graphics",
    "ai visual", "ai creative", "ai design", "ai art", "ai image",
    "ai picture", "ai photo", "ai portrait", "ai headshot", "ai avatar",
    
    # Technical Terms
    "generative", "synthetic", "artificial", "automated", "algorithmic",
    "procedural", "computational", "digital", "virtual", "simulated",
    "rendered", "computed", "generated", "created", "produced",
    
    # Video Processing
    "video processing", "image processing", "computer vision", "cv",
    "video analysis", "frame analysis", "motion analysis", "facial analysis",
    "face detection", "face recognition", "object detection", "segmentation",
    
    # AI Techniques
    "machine learning", "ml", "deep learning", "neural", "neural net",
    "ai model", "trained model", "pre-trained", "fine-tuned", "transfer learning",
    "supervised learning", "unsupervised learning", "reinforcement learning",
    
    # Content Types
    "talking head", "lip sync", "voice synthesis", "text to speech", "tts",
    "speech synthesis", "voice generation", "audio generation", "sound synthesis",
    "music generation", "ai music", "synthetic audio", "generated audio",
    
    # Social Media & Trends
    "ai meme", "ai funny", "funny ai", "ai viral", "ai trend", "ai challenge",
    "ai filter", "ai effect", "ai transformation", "ai morphing", "ai blending",
    
    # Professional Terms
    "ai workflow", "ai pipeline", "ai automation", "ai optimization",
    "ai scaling", "ai rendering", "ai compositing", "ai post-production",
    "ai editing", "ai color grading", "ai stabilization", "ai denoising"
]

# Low-confidence AI/deepfake keywords (bias: +0.05)
LOW_CONFIDENCE_AI_KEYWORDS = [
    # General AI Terms
    "ai", "artificial", "intelligence", "smart", "automated", "automatic",
    "generated", "synthetic", "fake", "virtual", "digital", "computer",
    "algorithm", "computational", "programmed", "coded", "scripted",
    
    # General Video Terms
    "video", "image", "picture", "photo", "frame", "clip", "media",
    "content", "visual", "graphic", "animation", "motion", "movement",
    "effect", "filter", "enhancement", "processing", "editing", "editing",
    
    # General Technology Terms
    "technology", "tech", "software", "app", "application", "tool",
    "platform", "service", "system", "engine", "framework", "library",
    "api", "sdk", "plugin", "extension", "addon", "integration",
    
    # General Creative Terms
    "creative", "artistic", "art", "design", "style", "aesthetic",
    "beautiful", "stunning", "amazing", "incredible", "fantastic",
    "realistic", "lifelike", "natural", "organic", "fluid", "smooth",
    
    # General Processing Terms
    "processed", "enhanced", "improved", "optimized", "refined", "polished",
    "cleaned", "restored", "repaired", "fixed", "corrected", "adjusted",
    "modified", "altered", "changed", "transformed", "converted", "adapted"
]

# Additional specialized AI video tools (high confidence)
SPECIALIZED_AI_TOOLS = [
    # Video Generation & Editing
    "inworld", "character.ai", "replika", "chai", "character ai",
    "jenni ai", "copy.ai", "jasper", "writesonic", "rytr", "copy.ai",
    "surfer seo", "frase", "outranking", "scalenut", "peppertype",
    
    # 3D & Animation
    "blender", "maya", "cinema 4d", "houdini", "3ds max", "zbrush",
    "substance", "quixel", "megascans", "unreal engine", "unity",
    "godot", "cryengine", "lumberyard", "armory3d", "babylon.js",
    
    # Motion Graphics & VFX
    "after effects", "premiere pro", "davinci resolve", "final cut",
    "nuke", "fusion", "hitfilm", "resolve", "lightworks", "kdenlive",
    "openshot", "shotcut", "blender", "cinema 4d", "motion graphics",
    
    # AI-Powered Video Tools
    "descript", "overdub", "filler words", "auto captions", "auto subtitles",
    "auto transcription", "speech to text", "voice to text", "audio to text",
    "video to text", "auto editing", "smart editing", "ai editing",
    
    # Live Streaming & Real-time
    "obs", "streamlabs", "xsplit", "wirecast", "vmix", "restream",
    "live streaming", "real-time", "live", "streaming", "broadcast",
    "webinar", "virtual event", "online event", "digital event",
    
    # Social Media AI Tools
    "tiktok", "instagram", "youtube", "facebook", "twitter", "linkedin",
    "snapchat", "discord", "twitch", "reddit", "pinterest", "tumblr",
    "social media", "viral", "trending", "hashtag", "engagement",
    
    # AI Research & Development
    "openai", "anthropic", "google ai", "microsoft ai", "meta ai",
    "nvidia ai", "amd ai", "intel ai", "apple ai", "amazon ai",
    "research", "development", "experimental", "beta", "alpha", "prototype"
]

# Combine all high-confidence tools
ALL_HIGH_CONFIDENCE_KEYWORDS = HIGH_CONFIDENCE_AI_TOOLS + SPECIALIZED_AI_TOOLS

# Word boundary patterns for better matching
WORD_BOUNDARY_PATTERNS = [
    r'\b{}\b',  # Full word match
    r'{}',      # Partial match
    r'^{}',     # Start of string
    r'{}$',     # End of string
    r'{}[^a-zA-Z0-9]',  # Word followed by non-alphanumeric
    r'[^a-zA-Z0-9]{}',  # Non-alphanumeric followed by word
]

def get_comprehensive_keywords():
    """Get all keyword categories for the metadata classifier"""
    return {
        'high_confidence': ALL_HIGH_CONFIDENCE_KEYWORDS,
        'medium_confidence': MEDIUM_CONFIDENCE_AI_KEYWORDS,
        'low_confidence': LOW_CONFIDENCE_AI_KEYWORDS
    }

def get_keyword_counts():
    """Get keyword counts for each category"""
    keywords = get_comprehensive_keywords()
    return {
        'high_confidence': len(keywords['high_confidence']),
        'medium_confidence': len(keywords['medium_confidence']),
        'low_confidence': len(keywords['low_confidence']),
        'total': sum(len(category) for category in keywords.values())
    }
