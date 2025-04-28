# 注意！本代码仍在调试阶段，建议按照documents中的audio_speaker.md进行测试！

'''
本代码包括：
1.读取麦克风\扬声器
2.提供测试,录制一段语音并将其播放出来
有关pykos.services.sound提供的类实现 ,请参考:
https://kscalelabs.github.io/api-docs/pykos/sound.html
'''

import asyncio
from io import BytesIO

from pykos import KOS
from pykos.services.sound import SoundServiceClient, AudioConfig

async def main():
    # 1. 连接
    # async with KOS(ip='localhost', port=50051) as kos:# kos-sim端使用本行，将下一行注释
    async with KOS(ip='192.168.42.1', port=50051) as kos:
        # 2. 初始化SoundServiceClient
        sound_client = SoundServiceClient(kos._channel)

        # 检查目前设备情况
        info = await sound_client.get_audio_info()
        print("Playback capabilities:", info.playback)
        print("Recording capabilities:", info.recording)

        # 3. 音频设置
        config = AudioConfig(
            sample_rate=44100,
            bit_depth=16,
            channels=1
        )

        # 4. 测试
        print("recording…")
        audio_buffer = BytesIO()
        async for chunk in sound_client.record_audio(
            duration_ms=5000, **config
        ):
            audio_buffer.write(chunk)
        print("recorded,", audio_buffer.tell(), "byte saved")
        audio_buffer.seek(0)
        print("playing…")
        async def audio_iterator():
            while True:
                data = audio_buffer.read(4096)
                if not data:
                    break
                yield data

        response = await sound_client.play_audio(
            audio_iterator(), **config
        )

        if response.success:
            print("test passed!")
        else:
            print("error:", response.error)

if __name__ == "__main__":
    asyncio.run(main())

'''
注:本测试使用回环测试,数据缓存在audio_buffer
如果你想把音频保存为wav,需要做如下修改：

import wave

在audio_buffer.seek(0)之后,插入写wav文件的逻辑

with wave.open('output_test01.wav', 'wb') as wf:
    wf.setnchannels(config.channels)
    wf.setsampwidth(config.bit_depth // 8)
    wf.setframerate(config.sample_rate)
    wf.writeframes(audio_buffer.read())

参考:https://stackoverflow.com/questions/52369925/creating-wav-file-from-bytes
'''