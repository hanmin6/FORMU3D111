from pydantic_settings import BaseSettings
from enum import Enum
from pathlib import Path
import os
from dotenv import load_dotenv

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

# 手动加载 .env 文件
load_dotenv(ENV_FILE)

class ServiceType(str, Enum):
	COZE="coze"
     

class Settings(BaseSettings):
	
	# COZE BASE_URL 
	COZE_BASE_URL: str
	COZE_AUTHORIZATION: str

	# 图片特征分析
	PICTURE_ANALYSIS_BOT_ID: str 

	# 可爱风格
	CUTE_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 蒸汽朋克风格
	STEAMPUNK_STYLE_PROMPT_GENERATION_BOT_ID: str
	
	# 日漫风格
	JAPANESE_COMIC_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 美漫风格
	AMERICAN_COMIC_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 职业风格
	PROFESSION_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 赛博朋克风格 
	CYBERPUNK_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 哥特风格
	GOTHIC_STYLE_PROMPT_GENERATION_BOT_ID: str

	# 写实风格
	REALISTIC_STYLE_PROMPT_GENERATION_BOT_ID: str

	# Database settings - 使用 Railway 标准环境变量名
	DB_HOST: str = "localhost"  # 默认值，Railway 会覆盖
	DB_PORT: int = 3306         # 默认值，Railway 会覆盖
	DB_USER: str = "root"       # 默认值，Railway 会覆盖
	DB_PASSWORD: str = ""       # 默认值，Railway 会覆盖
	DB_NAME: str = "FORMU"      # 默认值，Railway 会覆盖
	
	# Railway 标准环境变量名
	MYSQLHOST: str = "localhost"
	MYSQLPORT: int = 3306
	MYSQLUSER: str = "root"
	MYSQLPASSWORD: str = ""
	MYSQLDATABASE: str = "FORMU"


	# Tripo
	TRIPO_API_KEY: str

	# Sora 
	SORA_BASE_URL: str
	SORA_API_KEY: str


	@property
	def DATABASE_URL(self) -> str:
		# 优先使用 Railway 环境变量，如果没有则使用配置中的值
		db_host = os.getenv("MYSQLHOST", self.DB_HOST)
		db_user = os.getenv("MYSQLUSER", self.DB_USER)
		db_password = os.getenv("MYSQLPASSWORD", self.DB_PASSWORD)
		db_database = os.getenv("MYSQLDATABASE", self.DB_NAME)
		db_port = int(os.getenv("MYSQLPORT", self.DB_PORT))
		
		return f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"


	class Config:
		env_file = str(ENV_FILE)
		env_file_encoding = "utf-8"
		case_sensitive = True
		extra = "allow"  # 允许额外的环境变量 

settings = Settings() 