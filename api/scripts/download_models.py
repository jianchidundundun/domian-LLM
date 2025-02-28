import os
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download

def download_models():
    # 设置缓存目录
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # 设置环境变量
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.environ['HF_HOME'] = cache_dir
    
    try:
        # 下载模型
        print("正在下载模型...")
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=cache_dir
        )
        print("模型下载完成")
    except Exception as e:
        print(f"模型下载失败: {str(e)}")
        print("尝试下载备用模型...")
        model = SentenceTransformer(
            'paraphrase-MiniLM-L3-v2',
            cache_folder=cache_dir
        )

if __name__ == "__main__":
    download_models() 