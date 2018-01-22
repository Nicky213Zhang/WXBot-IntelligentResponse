import wave
import sys
noise_file3 = wave.open('noise_file3.wav','w')
noise_file3.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
values = []
for i in range(0,sample_len):
	value = random.randint(-32767, 32767)
	packed_vaule = struct.pack('h',value)
	values.append(packed_vaule)
	value_all = ''.join(values)
	noise_file3.writeframes(value_all)
	noise_file3.close()
	d4 = datetime.datetime.now()