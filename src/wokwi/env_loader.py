from dotenv import load_dotenv
import os
from SCons.Script import Import, ARGUMENTS

def add_api_url_flag(env):
	load_dotenv()
	api_url = os.getenv("API_URL")
	if api_url:
		# Garante que o valor será passado como string literal para o compilador
		api_url_str = api_url.strip('"')  # remove aspas se houver
		# env.Append(CCFLAGS=[f"'-D API_URL=\"{str(api_url_str)}\"'"])
		env.Append(BUILD_FLAGS=[f"'-D API_URL=\"{str(api_url_str)}\"'"])

def before_build(source, target, env):
	add_api_url_flag(env)

Import("env")
add_api_url_flag(env)