import openstack
import asyncio
import subprocess
import json

async def recover_vm(
		backup_image_path: str,
		vm_name: str,
		flavor_id: str,
		network_id: str
):
	# 1. OpenStack 연결
	conn = openstack.connect(
		auth_url="http://<keystone>:5000/v3",
		project_name="myproject",
		username="myuser",
		password="mypassword",
		user_domain_name="Default",
		project_domain_name="Default"
	)
	# 2. 이미지 포맷 확인 및 변환
	
	
	# 3. Glance에 이미지 등록

	# 4. 하이퍼바이저 리소스 확인

	# 5. Nova VM 생성

	pass

def get_image_info(filename):
	"""qemu-img로 이미지 정보 json으로 가져오기"""
	cmd = ['qemu-img', 'info', '--output=json', filename]
	try:
		result = subprocess.run(cmd, check=True, capture_output=True, text=True)
		info = json.loads(result.stdout)
		return info
	except subprocess.CalledProcessError as e:
		print(f"정보 가져오기 실패: {e.stderr}")
		return None

# convert_image('test_disk.qcow2', 'test_disk.raw')
def convert_image(source, dest, source_fmt='qcow2', dest_fmt='raw'):
	"""qemu-img로 이미지 변환"""

	cmd = ['qemu-img', 'convert', '-f', source_fmt, '-O', dest_fmt, source, dest]
	try:
		subprocess.run(cmd, check=True)
		print(f"변환 성공: {source} -> {dest}")
	except subprocess.CalledProcessError as e:
		print(f"변환 실패: {e.stderr}")

	