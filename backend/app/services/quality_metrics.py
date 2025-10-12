import re
import os
from typing import Dict, List

class QualityMetrics:
    def __init__(self):
        self._m = self._setup()
        
    def _setup(self):
        return {
            'a': [
                # Core AI terms
                'ai', 'artificial intelligence', 'ai generated', 'ai-generated', 'aigenerated',
                'ai video', 'ai-video', 'aivideo', 'ai_video', 'ai vid', 'aivid',
                'ai content', 'ai-content', 'aicontent', 'ai creation', 'ai made',
                'deepfake', 'deep fake', 'deep-fake', 'deepfakes', 'deep fakes',
                'fakeface', 'face swap', 'faceswap', 'face-swap', 'face swapping',
                'synthetic', 'synthetic video', 'synthetic media', 'synthesia',
                'fake', 'fake video', 'not real', 'notreal', 'unreal', 'artificial',
                'generated', 'generated video', 'auto generated', 'computer generated',
                'cg', 'cgi', 'made with ai', 'created with ai', 'produced with ai',
                'built with ai', 'designed with ai', 'not filmed', 'not recorded', 'virtual'
            ],
            'b': [
                # OpenAI Sora
                'sora', 'openai sora', 'sora ai', 'sora video', 'sora-ai', 'soraai',
                'sora generated', 'made with sora', 'created with sora', 'by sora',
                'sora demo', 'sora test', 'sora sample', 'sora output',
                # Google Veo
                'veo', 'veo3', 'veo 3', 'veo2', 'veo 2', 'google veo', 'veo ai',
                'veo video', 'veo generated', 'made with veo', 'by veo',
                # Runway
                'runway', 'runwayml', 'runway ml', 'runway ai', 'runway-ai',
                'gen-1', 'gen1', 'gen-2', 'gen2', 'gen-3', 'gen3',
                'runway gen', 'runway generated', 'made with runway',
                # Pika Labs
                'pika', 'pika labs', 'pika ai', 'pikalabs', 'pika_labs',
                'pika video', 'pika generated', 'made with pika', 'pika 1.0',
                # Luma AI
                'luma', 'luma ai', 'lumaai', 'luma dream', 'dream machine',
                'luma video', 'luma generated', 'made with luma',
                # Kling AI
                'kling', 'kling ai', 'klingai', 'kling video', 'kling generated',
                # Haiper
                'haiper', 'haiper ai', 'haiperai', 'haiper video', 'haiper generated',
                # Synthesia
                'synthesia', 'synthesia ai', 'synthesia video', 'synthesia avatar',
                # D-ID
                'd-id', 'did', 'd id', 'creative reality', 'd-id video', 'd-id avatar',
                # HeyGen
                'heygen', 'hey gen', 'hey-gen', 'heygen ai', 'heygen video', 'heygen avatar'
            ],
            'c': [
                # Midjourney
                'midjourney', 'mid journey', 'mid-journey', 'mj', 'midjourney ai',
                'midjourney v5', 'midjourney v6', 'midjourney v7', 'mj v5', 'mj v6',
                'midjourney generated', 'made with midjourney', 'midjourney art',
                # DALL-E
                'dalle', 'dall-e', 'dall e', 'dalle2', 'dalle3', 'dall-e 2', 'dall-e 3',
                'dalle generated', 'made with dalle', 'openai dalle',
                # Stable Diffusion
                'stable diffusion', 'stablediffusion', 'stable-diffusion', 'sd',
                'sd xl', 'sdxl', 'sd 1.5', 'sd 2.0', 'sd 2.1', 'sd 3.0',
                'stable diffusion video', 'sdv', 'sd video',
                # Leonardo AI
                'leonardo', 'leonardo ai', 'leonardo-ai', 'leonardoai',
                'leonardo generated', 'made with leonardo',
                # Ideogram
                'ideogram', 'ideogram ai', 'ideogram-ai', 'ideogramai',
                # Flux
                'flux', 'flux ai', 'flux-ai', 'flux.1', 'flux 1', 'flux pro',
                'flux generated', 'made with flux', 'black forest labs',
                # Adobe Firefly
                'firefly', 'adobe firefly', 'firefly ai', 'firefly generated'
            ],
            'd': [
                'neural network', 'neural-network', 'neuralnetwork', 'neural net', 'nn',
                'machine learning', 'machinelearning', 'ml', 'deep learning', 'deeplearning', 'dl',
                'diffusion model', 'diffusion-model', 'latent diffusion',
                'gan', 'generative adversarial network',
                'transformer', 'transformer model', 'vision transformer', 'vit',
                'neural rendering', 'neural-rendering',
                'text to video', 'text-to-video', 'text2video', 't2v', 'txt2vid',
                'image to video', 'image-to-video', 'img2vid', 'i2v',
                'video synthesis', 'video generation', 'ai animation', 'ai motion',
                'aftereffects', 'ae', 'adobe after effects', 'vfx', 'cgi'
            ],
            'e': [
                '#ai', '#aiart', '#aiartwork', '#aiartist', '#aiartcommunity',
                '#aivideo', '#aivideos', '#aivideocreator', '#aivideogeneration',
                '#aianimation', '#aianimated', '#deepfake', '#deepfakes',
                '#synthetic', '#syntheticmedia', '#aitools', '#generativeai', '#genai',
                '#sora', '#soraai', '#openaisora', '#veo', '#veo3', '#googleveo',
                '#runway', '#runwayml', '#gen2', '#gen3', '#midjourney', '#mj',
                '#dalle', '#dalle2', '#dalle3', '#stablediffusion', '#sd', '#sdxl',
                '#pika', '#pikalabs', '#luma', '#lumaai', '#kling', '#klingai',
                '#edit', '#edited', '#vfx', '#cgi', '#aftereffects', '#ae',
                '#trending', '#viral', '#fyp', '#foryou', '#animation', '#motion'
            ],
            'f': [
                'made with', 'made using', 'made by', 'created with', 'created using',
                'generated with', 'generated using', 'produced with', 'produced using',
                'built with', 'designed with', 'rendered with', 'powered by',
                'enhanced by', 'improved by', 'ai tool', 'ai model', 'ai system',
                'text prompt', 'prompt', 'ai assistance', 'ai assisted', 'with ai',
                'auto generated', 'automatically generated', 'computer generated',
                'not filmed', 'not recorded', 'virtual', 'digital only'
            ],
            'g': [
                'meta ai', 'meta video', 'anthropic', 'claude video',
                'cohere video', 'inflection ai', 'character.ai',
                'replicate', 'huggingface', 'civitai', 'tensor.art',
                'playground ai', 'nightcafe', 'artbreeder', 'wombo',
                'starryai', 'craiyon', 'bluewillow', 'gpt', 'gpt-4', 'gpt4', 'gpt 4',
                'chatgpt', 'chat gpt', 'claude', 'gemini', 'gemini pro', 'gemini ultra',
                'llm', 'large language model', 'foundation model', 'transformer',
                'diffusion', 'stable diffusion', 'midjourney', 'dalle', 'dall-e',
                'dalle2', 'dalle-2', 'dall-e 2', 'dalle3', 'dalle-3', 'dall-e 3',
                'imagen', 'imagen 2', 'imagen 3', 'parti', 'parti-3', 'parti 3',
                'muse', 'muse 2', 'muse 3', 'flamingo', 'flamingo-80b', 'flamingo 80b',
                'runway', 'runwayml', 'runway ml', 'gen-1', 'gen1', 'gen-2', 'gen2',
                'gen-3', 'gen3', 'gen-4', 'gen4', 'runway gen', 'runway generated',
                'made with runway', 'runway ai', 'runway-ai', 'runwayai',
                'synthesia', 'synthesia ai', 'synthesia video', 'synthesia avatar',
                'd-id', 'did', 'd id', 'creative reality', 'd-id video', 'd-id avatar',
                'heygen', 'hey gen', 'hey-gen', 'heygen ai', 'heygen video',
                'reface', 'reface ai', 'reface app', 'reface video', 'reface swap',
                'wombo', 'wombo ai', 'wombo dream', 'wombo video', 'wombo generated',
                'myheritage', 'my heritage', 'myheritage ai', 'myheritage video',
                'faceapp', 'face app', 'faceapp ai', 'faceapp video', 'faceapp filter',
                'snapchat', 'snap chat', 'snapchat filter', 'snapchat lens',
                'tiktok', 'tik tok', 'tiktok filter', 'tiktok effect',
                'instagram', 'insta', 'instagram filter', 'instagram story',
                'facebook', 'fb', 'facebook filter', 'facebook video',
                'youtube', 'yt', 'youtube shorts', 'youtube video',
                'midjourney', 'midjourney ai', 'midjourney bot', 'midjourney v5',
                'midjourney v6', 'midjourney v6', 'midjourney niji', 'midjourney niji 5',
                'midjourney niji 6', 'midjourney alpha', 'midjourney beta',
                'stable diffusion', 'stable-diffusion', 'stablediffusion',
                'sd', 'sd 1.5', 'sd 2.0', 'sd 2.1', 'sd 3.0', 'sd xl', 'sdxl',
                'automatic1111', 'a1111', 'comfyui', 'comfy ui', 'invoke ai',
                'novelai', 'novel ai', 'novel-ai', 'novelai image', 'novelai video',
                'leonardo', 'leonardo ai', 'leonardo-ai', 'leonardoai',
                'crayon', 'crayon ai', 'crayon-ai', 'crayonai',
                'nightcafe', 'night cafe', 'nightcafe ai', 'nightcafe studio',
                'artbreeder', 'art breeder', 'artbreeder ai', 'artbreeder image',
                'deepai', 'deep ai', 'deep-ai', 'deepai image', 'deepai video',
                'remove.bg', 'remove bg', 'removebg', 'remove background',
                'upscale', 'upscaling', 'ai upscale', 'ai upscaling',
                'esrgan', 'esr-gan', 'esr gan', 'real-esrgan', 'real esrgan',
                'waifu2x', 'waifu 2x', 'waifu-2x', 'waifu2x upscale',
                'neural network', 'neural net', 'neural-net', 'neuralnet',
                'deep learning', 'deep-learning', 'deeplearning',
                'machine learning', 'machine-learning', 'machinelearning', 'ml',
                'computer vision', 'computer-vision', 'computervision', 'cv',
                'natural language processing', 'nlp', 'nlp ai', 'nlp model',
                'transformer', 'transformer model', 'transformer architecture',
                'attention mechanism', 'attention', 'self-attention',
                'encoder', 'decoder', 'encoder-decoder', 'encoder decoder',
                'gan', 'generative adversarial network', 'gans', 'dcgan', 'dc-gan',
                'vae', 'variational autoencoder', 'variational auto-encoder',
                'autoencoder', 'auto-encoder', 'auto encoder',
                'lstm', 'long short-term memory', 'long short term memory',
                'gru', 'gated recurrent unit', 'gated recurrent units',
                'cnn', 'convolutional neural network', 'convolutional neural net',
                'rnn', 'recurrent neural network', 'recurrent neural net',
                'resnet', 'res-net', 'res net', 'residual network',
                'inception', 'inception net', 'inception network',
                'mobilenet', 'mobile net', 'mobile-network',
                'efficientnet', 'efficient net', 'efficient-network',
                'vision transformer', 'vit', 'vision-transformer',
                'swin transformer', 'swin-transformer', 'swin transformer',
                'convnext', 'conv-next', 'conv next', 'convolutional next',
                'yolo', 'you only look once', 'yolo v5', 'yolo v6', 'yolo v7', 'yolo v8',
                'detectron', 'detectron2', 'detectron 2',
                'mask r-cnn', 'mask rcnn', 'mask r cnn',
                'faster r-cnn', 'faster rcnn', 'faster r cnn',
                'retinanet', 'retina net', 'retina-network',
                'gpt', 'gpt-1', 'gpt-2', 'gpt-3', 'gpt-4', 'gpt-5',
                'gpt1', 'gpt2', 'gpt3', 'gpt4', 'gpt5',
                'gpt 1', 'gpt 2', 'gpt 3', 'gpt 4', 'gpt 5',
                'chatgpt', 'chat gpt', 'chat-gpt', 'chatgpt-3', 'chatgpt-4',
                'chatgpt3', 'chatgpt4', 'chat gpt 3', 'chat gpt 4',
                'claude', 'claude-1', 'claude-2', 'claude-3', 'claude-3.5',
                'claude1', 'claude2', 'claude3', 'claude 1', 'claude 2', 'claude 3',
                'anthropic', 'anthropic ai', 'anthropic claude',
                'gemini', 'gemini pro', 'gemini ultra', 'gemini nano',
                'gemini-pro', 'gemini-ultra', 'gemini-nano',
                'bard', 'google bard', 'bard ai', 'bard-ai',
                'palm', 'palm 2', 'palm2', 'palm-2', 'pathways language model',
                'lamda', 'lamda 2', 'lamda2', 'lamda-2', 'language model for dialogue',
                'laion', 'laion-400m', 'laion 400m', 'laion400m',
                'laion-5b', 'laion 5b', 'laion5b',
                'clip', 'clip model', 'contrastive language-image pre-training',
                'dall-e', 'dalle', 'dall-e 1', 'dall-e 2', 'dall-e 3',
                'dalle1', 'dalle2', 'dalle3', 'dalle 1', 'dalle 2', 'dalle 3',
                'imagen', 'imagen 1', 'imagen 2', 'imagen 3', 'imagen 4',
                'imagen1', 'imagen2', 'imagen3', 'imagen 1', 'imagen 2', 'imagen 3',
                'parti', 'parti-3', 'parti 3', 'parti3', 'pathways autoregressive text-to-image',
                'muse', 'muse 1', 'muse 2', 'muse 3', 'muse1', 'muse2', 'muse3',
                'muse 1', 'muse 2', 'muse 3', 'masked generative sequence transformer',
                'flamingo', 'flamingo-80b', 'flamingo 80b', 'flamingo80b',
                'few-shot learning', 'few shot learning', 'fewshot learning',
                'openai', 'open ai', 'open-ai', 'openai api', 'openai gpt',
                'anthropic', 'anthropic ai', 'anthropic claude', 'anthropic api',
                'google ai', 'google-ai', 'googleai', 'google research',
                'deepmind', 'deep mind', 'deep-mind', 'google deepmind',
                'meta ai', 'meta-ai', 'metaai', 'facebook ai', 'facebook research',
                'microsoft ai', 'microsoft-ai', 'microsoftai', 'microsoft research',
                'nvidia ai', 'nvidia-ai', 'nvidiaai', 'nvidia research',
                'hugging face', 'huggingface', 'hugging-face', 'hf', 'transformers',
                'replicate', 'replicate ai', 'replicate-ai', 'replicateai',
                'runpod', 'runpod ai', 'runpod-ai', 'runpodai',
                'vast.ai', 'vast ai', 'vast-ai', 'vastai',
                'colab', 'google colab', 'colaboratory', 'google colaboratory',
                'kaggle', 'kaggle ai', 'kaggle-ai', 'kaggleai',
                'gradio', 'gradio ai', 'gradio-ai', 'gradioai',
                'streamlit', 'streamlit ai', 'streamlit-ai', 'streamlitai',
                'jupyter', 'jupyter notebook', 'jupyter lab', 'jupyterhub',
                'arxiv', 'arxiv paper', 'arxiv preprint', 'arxiv publication',
                'neurips', 'neurips 2023', 'neurips 2024', 'neurips conference',
                'icml', 'icml 2023', 'icml 2024', 'icml conference',
                'iclr', 'iclr 2023', 'iclr 2024', 'iclr conference',
                'aaai', 'aaai 2023', 'aaai 2024', 'aaai conference',
                'ijcai', 'ijcai 2023', 'ijcai 2024', 'ijcai conference',
                'acl', 'acl 2023', 'acl 2024', 'acl conference',
                'emnlp', 'emnlp 2023', 'emnlp 2024', 'emnlp conference',
                'naacl', 'naacl 2023', 'naacl 2024', 'naacl conference',
                'cvpr', 'cvpr 2023', 'cvpr 2024', 'cvpr conference',
                'iccv', 'iccv 2023', 'iccv 2024', 'iccv conference',
                'eccv', 'eccv 2023', 'eccv 2024', 'eccv conference',
                'siggraph', 'siggraph 2023', 'siggraph 2024', 'siggraph conference',
                'chi', 'chi 2023', 'chi 2024', 'chi conference',
                'uist', 'uist 2023', 'uist 2024', 'uist conference',
                'interact', 'interact 2023', 'interact 2024', 'interact conference',
                'fine-tuning', 'fine tuning', 'finetuning', 'fine-tuned', 'fine tuned',
                'transfer learning', 'transfer-learning', 'transferlearning',
                'few-shot', 'few shot', 'fewshot', 'zero-shot', 'zero shot', 'zeroshot',
                'one-shot', 'one shot', 'oneshot', 'multi-shot', 'multi shot', 'multishot',
                'prompt engineering', 'prompt-engineering', 'promptengineering',
                'prompt', 'prompting', 'prompt design', 'prompt-design',
                'chain of thought', 'chain-of-thought', 'chainofthought', 'cot',
                'instruction tuning', 'instruction-tuning', 'instructiontuning',
                'reinforcement learning', 'reinforcement-learning', 'reinforcementlearning',
                'rlhf', 'rl hf', 'rl-hf', 'reinforcement learning from human feedback',
                'constitutional ai', 'constitutional-ai', 'constitutionalai',
                'constitutional training', 'constitutional-training',
                'safety training', 'safety-training', 'safetytraining',
                'alignment', 'ai alignment', 'ai-alignment', 'aialignment',
                'robustness', 'model robustness', 'model-robustness',
                'interpretability', 'model interpretability', 'model-interpretability',
                'explainability', 'model explainability', 'model-explainability',
                'bias', 'model bias', 'model-bias', 'algorithmic bias',
                'fairness', 'model fairness', 'model-fairness', 'algorithmic fairness',
                'privacy', 'model privacy', 'model-privacy', 'differential privacy',
                'federated learning', 'federated-learning', 'federatedlearning',
                'distributed training', 'distributed-training', 'distributedtraining',
                'gradient descent', 'gradient-descent', 'gradientdescent',
                'adam', 'adam optimizer', 'adam-optimizer', 'adamoptimizer',
                'sgd', 'stochastic gradient descent', 'stochastic-gradient-descent',
                'momentum', 'nesterov momentum', 'nesterov-momentum',
                'rmsprop', 'rms prop', 'rms-prop', 'root mean square propagation',
                'adagrad', 'ada grad', 'ada-grad', 'adaptive gradient',
                'adadelta', 'ada delta', 'ada-delta', 'adaptive delta',
                'adamax', 'ada max', 'ada-max', 'adaptive max',
                'nadam', 'n adam', 'n-adam', 'nesterov adam',
                'learning rate', 'learning-rate', 'learningrate', 'lr',
                'batch size', 'batch-size', 'batchsize', 'mini-batch', 'minibatch',
                'epoch', 'epochs', 'training epoch', 'training-epoch',
                'validation', 'validation set', 'validation-set', 'validationset',
                'test set', 'test-set', 'testset', 'testing set', 'testing-set',
                'overfitting', 'over-fitting', 'overfitting', 'underfitting', 'under-fitting',
                'regularization', 'regularization technique', 'regularization-technique',
                'dropout', 'drop-out', 'drop out', 'dropout layer', 'dropout-layer',
                'batch normalization', 'batch-normalization', 'batchnormalization', 'batchnorm',
                'layer normalization', 'layer-normalization', 'layernormalization', 'layernorm',
                'weight decay', 'weight-decay', 'weightdecay', 'l2 regularization', 'l2-regularization',
                'l1 regularization', 'l1-regularization', 'l1regularization', 'lasso',
                'early stopping', 'early-stopping', 'earlystopping',
                'data augmentation', 'data-augmentation', 'dataaugmentation',
                'cross validation', 'cross-validation', 'crossvalidation', 'k-fold', 'kfold',
                'hyperparameter tuning', 'hyperparameter-tuning', 'hyperparametertuning',
                'grid search', 'grid-search', 'gridsearch',
                'random search', 'random-search', 'randomsearch',
                'bayesian optimization', 'bayesian-optimization', 'bayesianoptimization',
                'genetic algorithm', 'genetic-algorithm', 'geneticalgorithm',
                'evolutionary algorithm', 'evolutionary-algorithm', 'evolutionaryalgorithm'
            ]
        }
    
    def calculate(self, path: str, data: dict) -> float:
        _x1 = 0.0
        _x2 = 0.0
        _x3 = 0.0
        
        _t1 = data.get('title', '') if data else ''
        _t2 = data.get('description', '') if data else ''
        _f1 = os.path.basename(path).lower()
        _frame_txt = self._extract_frame_text(path)
        
        _txt = f"{_t1} {_t2} {_f1} {_frame_txt}".lower()
        _txt = re.sub(r'[^\w\s#@]', ' ', _txt)
        
        for _cat, _items in self._m.items():
            for _item in _items:
                if _item in _txt:
                    _w = {'a': 1.0, 'b': 0.95, 'c': 0.9, 'd': 0.85, 'e': 0.8, 'f': 0.75, 'g': 0.7}
                    _x1 += _w.get(_cat, 0.5)
        
        _patterns = [
            (r'\bai\s+generated?\b', 1.0),
            (r'\bdeep\s*fake\b', 1.0),
            (r'\b(veo|sora|midjourney|runway|pika|luma|kling|haiper)\s*(v\d+|pro|demo)?\b', 0.95),
            (r'\bnot\s+real\b', 0.95),
            (r'\bfake\s+video\b', 0.95),
            (r'\bai\s+video\b', 0.9),
            (r'\bai\s+art\b', 0.8),
            (r'\bmade\s+with\s+(sora|veo|runway|pika|luma|ai)\b', 0.95),
            (r'\bcreated\s+with\s+(sora|veo|runway|pika|luma|ai)\b', 0.95),
            (r'\bgenerated\s+by\s+(sora|veo|runway|pika|luma|ai)\b', 0.95),
            (r'\b#ai\b', 0.7),
            (r'\b#aiart\b', 0.8),
            (r'\b#aivideo\b', 0.9),
            (r'\b#deepfake\b', 0.95),
            (r'\b#sora\b', 0.9),
            (r'\b#veo\b', 0.9),
            (r'\b#runway\b', 0.9),
            (r'\b#edit\b', 0.4),
            (r'\b#aftereffects\b', 0.5),
            (r'\b#trending\b', 0.3)
        ]
        
        for _pat, _w in _patterns:
            if re.search(_pat, _txt, re.IGNORECASE):
                _x2 += _w
        
        _fn_patterns = [
            r'(sora|veo|midjourney|runway|pika|luma)',
            r'(ai_|gen_|synth_|fake_)',
            r'(deepfake|ai_generated|synthetic)'
        ]
        
        for _pat in _fn_patterns:
            if re.search(_pat, _f1, re.IGNORECASE):
                _x3 += 0.8
        
        _total = _x1 + _x2 + _x3
        return min(_total / 3.0, 1.0)
    
    def _extract_frame_text(self, path: str) -> str:
        try:
            import cv2
            try:
                import pytesseract
            except:
                return ""
            
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return ""
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames_to_check = [
                int(total_frames * 0.1),
                int(total_frames * 0.5),
                int(total_frames * 0.9)
            ]
            
            extracted_text = ""
            for frame_num in frames_to_check:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if ret:
                    text = pytesseract.image_to_string(frame)
                    extracted_text += " " + text.lower()
            
            cap.release()
            return extracted_text
        except:
            return ""
