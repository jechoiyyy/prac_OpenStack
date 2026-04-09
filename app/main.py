import os
import subprocess
import openstack
import asyncio
import json
from functools import partial

async def recover_vm(
		backup_image_path: str,
		vm_name: str,
		flavor_id: str,
		network_id: str,
		required_vcpu: int,
		required_ram_mb: int,
		required_disk_gb: int,
):
	# asyncio.to_thread(func, *args, **kwargs)
	# 1. OpenStack 연결
	conn = await asyncio.to_thread(
		openstack.connect,
		auth_url="http://<keystone>:5000/3",
		project_name="myproject",			username="myuser",			password="mypassword",
		user_domain_name="Default",
		project_domain_name="Default"
	)

	# 2. 이미지 포맷 확인 및 변환
	converted_path = backup_image_path + ".qcow2"
	info_result = await asyncio.to_thread(get_image_info, backup_image_path)
	# info_result = await loop.run_in_executor(None, get_image_info, backup_image_path)
	if info_result is None:
		raise RuntimeError(f"이미지 정보를 읽을 수 없을 수 없습니다: {backup_image_path}")
	if info_result["format"] != "qcow2":
		await asyncio.to_thread(convert_image,backup_image_path, converted_path)
	else:
		converted_path = backup_image_path
	
	# 3. Glance에 이미지 등록
	image = await asyncio.to_thread(
		conn.image.create_image,
		name=f"{vm_name}-recovery-image",
		disk_format="qcow2",
		container_format="bare",
		visibility="private"
	)
	with open(converted_path, "rb") as f:
		await asyncio.to_thread(conn.image.upload_image, image.id, f)
	await asyncio.to_thread(conn.image.wait_for_image, image, status="active")

	# 4. 하이퍼바이저 리소스 확인
	stats = await asyncio.to_thread(conn.compute.get_hypervisor_statistics)
	print(f"Free vCPUs: {stats.vcpus - stats.vcpus_used}")
	print(f"Free RAM: {stats.memory_free_mb} MB")
	print(f"Free Disk: {stats.disk_available_least_gb} GB")

	if (stats.vcpus - stats.vcpus_used) < required_vcpu:
		raise RuntimeError("사용 가능한 vCPU가 부족합니다.")
	if stats.memory_free_mb < required_ram_mb:
		raise RuntimeError("사용 가능한 메모리가 부족합니다.")
	if stats.disk_free_gb < required_disk_gb:
		raise RuntimeError("사용 가능한 디스크 용량이 부족합니다.")

	# 5. Nova VM 생성
	server = await asyncio.to_thread(
		conn.compute.create_server,
		name=vm_name,
		image_id=image.id,
		flavor_id=flavor_id,
		networks=[{"uuid": network_id}]
	)

	# VM이 ACTIVE 상태가 될 때까지 대기
	server = await asyncio.to_thread(conn.compute.wait_for_server, server)
	print(f"VM 생성 완료: {server.name} (ID: {server.id}, Status: {server.status})")
	return server

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
def convert_image(source, dest, source_fmt='raw', dest_fmt='qcow2'):
	"""qemu-img로 이미지 변환"""

	cmd = ['qemu-img', 'convert', '-f', source_fmt, '-O', dest_fmt, source, dest]
	try:
		subprocess.run(cmd, check=True)
		print(f"변환 성공: {source} -> {dest}")
	except subprocess.CalledProcessError as e:
		print(f"변환 실패: {e.stderr}")
