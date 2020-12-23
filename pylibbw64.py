##  tools for bw64 file type
import io


def bytesValue(p:int, n:int) -> bytes:
  return p.to_bytes(n, byteorder='little', signed=False)

def fourCC(p:bytes) -> bytes:
  return bytesValue((p[3] << 24) | (p[2] << 16) | (p[1] << 8) | p[0], 4)


class Chunk:
  """ RIFF chunk base class """

  def __init__(self) -> None:
      self.id : bytes= b''
      self.size : int = 0
      self.data : bytes = b''


class ExtraData():
  """
    Class representation of the ExtraData of a FormatInfoChunk
  """

  def __init__(self, validBitsPerSample:int, dwChannelMask:int, subFormat:int, subFormatString:bytes) -> None:
      super().__init__()
      self.validBitsPerSample : int = validBitsPerSample
      self.dwChannelMask : int = dwChannelMask
      self.subFormat : int = subFormat
      self.subFormatString : bytes = subFormatString


class FormatInfoChunk(Chunk):
  """
    Simple FormatInfoChunk constructor
    param:
      channels:   number of channels
      sampleRate: sample rate of the audio data
      bitDepth:   bit depth used in file
      extraData:  custom ExtraData (optional, null if no custom)
  """

  def __init__(self, channels:int, sampleRate:int, bitDepth:int,
               extraData:ExtraData = None) -> None:
    super().__init__()
    self.id = fourCC(b"fmt ")
    self.size = 16    
    self.formatTag : int = 1
    self.channelCount : int = channels
    self.sampleRate : int = sampleRate
    self.bitPerSample : int = bitDepth
    self.extraData : ExtraData = extraData

    # validation
    if self.channelCount < 1:
      raise ValueError("channelCount < 1")

    if self.sampleRate < 1:
      raise ValueError("sampleRate < 1")

    if self.bitPerSample not in [16, 24, 32]:
      raise ValueError("bitDepth not supported: " + str(self.bitPerSample))

    self.data = bytesValue(self.formatTag, 2) \
              + bytesValue(self.channelCount, 2) \
              + bytesValue(self.sampleRate, 4) \
              + bytesValue(self.bytesPerSecond, 4) \
              + bytesValue(self.blockAlignment, 2) \
              + bytesValue(self.bitPerSample, 2)
    if self.extraData is not None:
      self.data += bytesValue(self.extraData.validBitsPerSample, 2) \
                 + bytesValue(self.extraData.dwChannelMask, 4) \
                 + bytesValue(self.extraData.subFormat, 2) \
                 + self.extraData.subFormatString           

  @property
  def blockAlignment(self) -> int:
    return self.channelCount * self.bitPerSample // 8

  @property
  def bytesPerSecond(self) -> int:
    return self.sampleRate * self.blockAlignment


class DataChunk(Chunk):
  """
    Class representation of a DataChunk
  """

  def __init__(self) -> None:
    super().__init__()
    self.id = fourCC(b"data")


class JunkChunk(Chunk):
  def __init__(self) -> None:
    super().__init__()
    self.id = fourCC(b"JUNK")
    self.size = 28
    self.data = bytes(self.size)


class AxmlChunk(Chunk):
  """
    Class representation of an AxmlChunk
  """

  def __init__(self, axml:bytes) -> None:
    super().__init__()
    self.id = fourCC(b"axml")
    self.size = len(axml)
    self.data = axml


class DbmdChunk(Chunk):
  """
    Class representation of a DbmdChunk
  """

  def __init__(self, dbmd:bytes) -> None:
    super().__init__()
    self.id = fourCC(b"dbmd")
    self.size = len(dbmd)
    self.data = dbmd 


class AudioId:
  """
    Class representation of an AudioId field
  """

  def __init__(self, trackIndex:int, uid:bytes, trackRef:bytes, packRef:bytes) -> None:
    super().__init__()
    if len(uid) > 12:
      raise RuntimeError("uid is too long ")
    if len(trackRef) > 14:
      raise RuntimeError("trackRef is too long ")
    if len(packRef) > 11:
      raise RuntimeError("packRef is too long ")

    self.trackIndex = trackIndex
    self.uid = uid.ljust(12)
    self.trackRef = trackRef.ljust(14)
    self.packRef = packRef.ljust(11)
    self.data:bytes = bytesValue(self.trackIndex, 2) + self.uid + self.trackRef + self.packRef + b' '

  def __eq__(self, o: object) -> bool:
    return self.data == o.data

  def __ne__(self, o: object) -> bool:
      return self.data != o.data


class ChnaChunk(Chunk):
  """
    Class representation of a ChnaChunk
  """

  def __init__(self, audioIds:AudioId) -> None:
    super().__init__()
    self.id = fourCC(b"chna")
    self.size = 
    self.audioIds = AudioId


extra = ExtraData(30, 99, 222, b'BWFF')
fmtchunk = FormatInfoChunk(2, 48000, 24, extra)
print("formatTag: {}\n channelCount: {}\n sampleRate: {}\n blockAlignment: {}\n extra_subFormat: {}\n".format(
  fmtchunk.formatTag, fmtchunk.channelCount, fmtchunk.sampleRate, fmtchunk.blockAlignment, fmtchunk.extraData.subFormatString))

pf = open('test.bin', 'wb')
pf.write(fmtchunk.id)
pf.write(bytesValue(fmtchunk.size, 4))
pf.write(fmtchunk.data)
pf.close()