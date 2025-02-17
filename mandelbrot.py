#!/bin/env python

""" The mandelbrot application is building a colorized Mandelbrot set image
"""

#############################################################################
#
#  The mandelbrot application is building a colorized Mandelbrot set fractal
#  images
#
#  Copyright 2011 by DIRAC Project
#  http://diracgrid.org
#
#############################################################################

#############################################################################
#
# Helper classes and functions
#
#############################################################################

####################################################
# BmpImage class derived from:
# py_kohn_bmp - Copyright 2007 by Michael Kohn
# http://www.mikekohn.net/
# mike@mikekohn.net
####################################################

class BmpImage:

  def __init__(self,filename,width,height,depth):

    self.out = 0
    self.width = width
    self.height = height
    self.depth = depth
    self.bytes = 0
    self.xpos = 0
    self.width_bytes = width*depth

    if (self.width_bytes%4)!=0:
      self.width_bytes=self.width_bytes+(4-(self.width_bytes%4))

    self.out=open(filename,"wb")
    self.out.write("BM")          # magic number
    if depth==1:
      self.write_int((self.width_bytes*height)+54+1024)
    else:
      self.write_int((self.width_bytes*height)+54)
    self.write_word(0)
    self.write_word(0)
    if depth==1:
      self.write_int(54+1024)
    else:
      self.write_int(54)

    self.write_int(40)                 # header_size
    self.write_int(width)              # width
    self.write_int(height)             # height
    self.write_word(1)                 # planes
    self.write_word(depth*8)           # bits per pixel
    self.write_int(0)                  # compression
    self.write_int(self.width_bytes*height*depth) # image_size
    self.write_int(0)                  # biXPelsperMetre
    self.write_int(0)                  # biYPelsperMetre

    if depth==1:
      self.write_int(256)              # colors used
      self.write_int(256)              # colors important

      for c in range(256):
        self.out.write('%c' % c)
        self.out.write('%c' % c)
        self.out.write('%c' % c)
        self.out.write('%c' % 0)

    else:
      self.write_int(0)                # colors used - 0 since 24 bit
      self.write_int(0)                # colors important - 0 since 24 bit

  def write_int(self,n):
     str_out='%c%c%c%c' % ((n&255),(n>>8)&255,(n>>16)&255,(n>>24)&255)
     self.out.write(str_out)

  def write_word(self,n):
     str_out='%c%c' % ((n&255),(n>>8)&255)
     self.out.write(str_out)

  def write_pixel_bw(self,y):
    self.out.write(str("%c" % y))
    self.xpos=self.xpos+1
    if self.xpos==self.width:
      while self.xpos<self.width_bytes:
        self.out.write(str("%c" % 0))
        self.xpos=self.xpos+1
      self.xpos=0

  def write_pixel(self,red,green,blue):
    self.out.write(str("%c" % (blue&255)))
    self.out.write(str("%c" % (green&255)))
    self.out.write(str("%c" % (red&255)))
    self.xpos=self.xpos+1
    if self.xpos==self.width:
      self.xpos=self.xpos*3
      while self.xpos<self.width_bytes:
        self.out.write(str("%c" % 0))
        self.xpos=self.xpos+1
      self.xpos=0

  def close(self):
    self.out.close()

def mandelbrot(c,maxCount = 100,limit=2):
  """ The main Mandelbrot set engine
  """
  z=complex(0,0)
  count = 0
  while count < maxCount:
    z=(z*z)+c
    #if checkCardioid(z):
    #  return maxCount
    if abs(z)>limit: break
    count += 1

  return count

def checkCardioid(c):
  """ Check getting to the Mandelbrot set area to stop iterations
  """
  x = c.real
  y = c.imag
  y2 = y*y
  q = (x-0.25)*(x-0.25) + y2
  qq = q*(q+(x-0.25))

  if qq < 0.25*y2:
    print ("exit 1")
    print (x,y,y2,q,qq,0.25*y2)
    return 1

  if (x+1)*(x+1)+y2 < 0.0625:
    print ("exit 2")
    print ( (x+1)*(x+1)+y2)
    return 1
  return 0

##########################################################
#
# Various color generators
#
##########################################################

def getColorRange(count,maxIter):
  black = [0,0,0]
  mincolor = [255.,255.,0.]
  maxcolor = [0.,0.,255.]

  color = [0,0,0]
  if count < maxIter:
    color = []
    for i in range(3):
      c = (maxcolor[i]*count + mincolor[i]*(maxIter-count))/maxIter
      color.append(int(c))
  return color

colorDict = {}

def getColorRandom(count,maxIter):
  global colorDict
  import md5
  key = "randomname"
  myMD5 = md5.md5()
  if not count in colorDict:
    myMD5.update( str(count)+key )
    hexstring = myMD5.hexdigest()
    color = [int('0x'+hexstring[:2],0),int('0x'+hexstring[2:4],0),int('0x'+hexstring[4:6],0)]
    colorDict[count] = color
  else:
    color = colorDict[count]
  return color

def getColorSlider(count,maxIter):
  global colorDict
  if count == maxIter:
    return [0,0,0]
  if not count in colorDict:
    color = []
    color.append(int(255./maxIter*count))
    color.append(int(255./maxIter*count))
    color.append(int(255. - 255./maxIter*count))
    colorDict[count] = color
  else:
    color = colorDict[count]
  return color

def getColorSin(count,maxIter):
  global colorDict,cFactor,cPhase,cDelta
  if count == maxIter:
    return [0,0,0]
  if not count in colorDict:
    arg = count*cFactor
    c1 = int(127.*(sin(arg+cPhase) + 1.))
    c2 = int(127.*(sin(arg+cPhase+cDelta) + 1.))
    c3 = int(127.*(sin(arg+cPhase+2.*cDelta) + 1.))
    color = [c1,c2,c3]
    colorDict[count] = color
  else:
    color = colorDict[count]
  return color

greyDict = {}

def getGreyLevel(count,maxIter, cFactor=0.02, cPhase=1.):
  global greyDict
  if count == maxIter:
    return 0
  if not count in greyDict:
    arg = count*cFactor
    grey = int(127.*(sin(arg+cPhase) + 1.))
    greyDict[count] = grey
  else:
    grey = greyDict[count]
  return grey

###################################################################
#
# Start of the main body
#
###################################################################

import time
import sys
import getopt
from math import sin

def usage():

  print ("""
  The mandelbrot program is creating an image of a Mandelbrot set and its vicinity in
  the given range of the C parameter. For more information about the Mandelbrot set
  see http://en.wikipedia.org/Mandelbrot.

  Usage:
      mandelbrot [options] [<output_file>]

  Options:
      -X, --cx - the real part of the C parameter in the center of the image, default = -0.5
      -Y, --cy - the imaginary part of the C parameter in the center of the image, default = 0.0
      -P, --precision - the step size of the C parameter increment per pixel of the image, default = 0.01
      -M, --max_iterations - the maximum number of the mandelbrot algorithm iterations, default = 100
      -W, --width - image width in pixels, default = 300
      -H, --height - image height in pixels, default = 300
      -B, --bw - force black and white image, default is a color image
      -F, --color_factor - color palette parameter defining how quickly the colors are changing, the value
                           should be in the range 0.<x<1.0, default = 0.02
      -S, --color_phase - a magic color palette parameter, default = 1.0
      -D, --color_delta - yet another magic color palette parameter, default = 1.0
      -h, --help - print this usage info
  """)

if __name__ == '__main__':
    # Get the command line options first
    options = ['width=','height=','cx=','cy=','precision=', 'start_line', 'n_lines', 'max_iterations=',
               'color_factor=','color_phase=','color_delta=','bw','help']
    optlist,args = getopt.getopt(sys.argv[1:], 'W:H:X:Y:P:L:N:M:F:S:D:Bh',options)

    # 4K  3840  x 2160
    # 8K  7680  x 4320
    # 16K 15360 x 8640 
    (image_width, image_height) = (7680, 4320)
    centerX = -0.5
    centerY = 0.0
    precision = .01
    cFactor = 0.02
    cPhase = 1.
    cDelta = 1.
    maxIter = 500
    output = 'out.bmp'
    bwImage = False
    start_line = 0
    n_lines = image_height

    for o,v in optlist:
      if o in ['-W','--width']:
        image_width = int(v)
      if o in ['-H','--height']:
        image_height = int(v)
      if o in ['-X','--cx']:
        centerX = float(v)
      if o in ['-Y','--cy']:
        centerY = float(v)
      if o in ['-P','--precision']:
        precision = float(v)

      if o in ['-L','--start_line']:
        start_line = int(v)*200
      if o in ['-N','--n_lines']:
        n_lines = int(v)

      if o in ['-F','--color_factor']:
        cFactor = float(v)
      if o in ['-S','--color_phase']:
        cPhase = float(v)
      if o in ['-D','--color_delta']:
        cDelta = float(v)
      if o in ['-M','--max_iterations']:
        maxIter = int(v)
      if o in ['-B','--bw']:
        bwImage = True
      if o in ['-h','--help']:
        usage()
        sys.exit(0)

    #if args:
      #output = args[0]

    output = 'data_'+str(start_line)+'.bmp'

    #centerX = -0.46490
    #centerY = -.56480
    #precision = .000002

    start_real = centerX - image_width*precision/2.
    start_imag = centerY - image_height*precision/2.
    end_real = centerX + image_width*precision/2.
    end_imag = centerY + image_height*precision/2.

    depth = 3
    if bwImage:
      depth = 1
    my_bmp=BmpImage(output,image_width,image_height,depth)

    inc_real=(end_real-start_real)/image_width
    inc_imag=(end_imag-start_imag)/image_height

    start=complex(start_real,start_imag)
    end=complex(end_real,end_imag)

    start = time.time()

    print ("max iterations: %s, precision: %s, C: %f+%fj" % (maxIter, precision, centerX,centerY))

    buff=list()
    # for y in range(image_height):
    y_i = start_line
    y_f = min(start_line + n_lines, image_height)
    print(y_i, y_f)
    for y in range(y_i, y_f):
      print('%d\r'%y)
      dump='%d' % y
      for x in range(image_width):
        c = complex(start_real+(inc_real*x),start_imag+(inc_imag*y))
        count = mandelbrot(c,maxIter)
        dump+=' %d' % count

        if bwImage:
          grey = getGreyLevel(count,maxIter)
          my_bmp.write_pixel_bw(grey)
        else:
          color = getColorSin(count,maxIter)
          my_bmp.write_pixel(*color)
          #print count, color, c
      buff.append(dump+'\n')

    print ('Image generation time %.2f' % (time.time()-start))

    my_bmp.close()

    open('data_%d.txt'%start_line,'w').writelines(buff)

