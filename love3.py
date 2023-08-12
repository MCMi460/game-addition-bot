# Created by Deltaion Lee (MCMi460) on Github
# Grab icons and title information from IDBE database

# A solid afternoon was spent. :D

# Thank you to 3DBrew's IDBE page (https://www.3dbrew.org/wiki/IDBE)

from Cryptodome.Cipher import AES
import Cryptodome.Cipher.AES
from binascii import hexlify, unhexlify
import requests, io, math, json, os
from PIL import Image

def getTitleData(titleID:hex):
	data = requests.get('https://idbe-ctr.cdn.nintendo.net/icondata/10/%s.idbe' % titleID.zfill(16), verify = False).content

	IV = unhexlify('A46987AE47D82BB4FA8ABC0450285FA4')

	K0 = unhexlify('4AB9A40E146975A84BB1B4F3ECEFC47B')
	K1 = unhexlify('90A0BB1E0E864AE87D13A6A03D28C9B8')
	K2 = unhexlify('FFBB57C14E98EC6975B384FCF40786B5')
	K3 = unhexlify('80923799B41F36A6A75FB8B48C95F66F')

	AES_KEYS = [K0, K1, K2, K3]

	key = AES_KEYS[data[1]]

	decipher = AES.new(key,AES.MODE_CBC,IV)

	return decipher.decrypt(data[2:])

def getTitleInfo(titleID:hex):
	if isinstance(titleID, str) and '0x' in titleID:
		titleID = int(titleID, 16)
	titleID = str(titleID)
	try:
		int(titleID, 16) # Errors if not HEX
	except:
		return None
	if isinstance(titleID, str):
		titleID = hex(int(titleID)).replace('0x', '')

	titleID = titleID.zfill(16).upper()

	try:
		data = getTitleData(titleID)
	except:
		return None

	ret = ''

	languages = [
		'Japanese',
		'English',
		'French',
		'German',
		'Italian',
		'Spanish',
		'Simplified Chinese',
		'Korean',
		'Dutch',
		'Portuguese',
		'Russian',
		'Traditional Chinese',
	]

	for i in range(12):
		offset = 0x50 + i * 0x200

		n = data[offset:offset+0x200]
		short = n[0x00:0x00+0x80].decode('utf-16').replace('\x00', '')
		long = n[0x80:0x80+0x100].decode('utf-16').replace('\x00', '')
		publisher = n[0x180:0x180+0x80].decode('utf-16').replace('\x00', '')

		ret += '## %s\n**Short:** %s\n**Long:** %s\n**Publisher:** %s\n' % (languages[i], short, long, publisher)

	icon_data = data[0x24D0:0x24D0+0x1200] # 48x48 icon data

	# Taken from Repo3DS (https://github.com/Repo3DS/shop-cache/blob/master/TitleInfo.py)
	(w, h) = (48, 48)
	tiled_icon = Image.frombuffer('RGB', (w, h), icon_data, 'raw', 'BGR;16')
	# Untile the image
	tile_order = [0,1,8,9,2,3,10,11,16,17,24,25,18,19,26,27,4,5,12,13,6,7,14,15,20,21,28,29,22,23,30,31,32,33,40,41,34,35,42,43,48,49,56,57,50,51,58,59,36,37,44,45,38,39,46,47,52,53,60,61,54,55,62,63]
	icon = Image.new('RGB', (w, h))
	pos = 0
	for y in range(0, h, 8):
		for x in range(0, w, 8):
			for k in range(8 * 8):
				xoff = tile_order[k] % 8
				yoff = int((tile_order[k] - xoff) / 8)

				posx = pos % w
				posy = math.floor(pos / w)
				pos += 1

				pixel = tiled_icon.getpixel((posx, posy))
				icon.putpixel((x + xoff, y + yoff), pixel)

	image_data = io.BytesIO()
	icon.save(image_data, format = 'PNG')
	image_data.seek(0)

	return ret, image_data
