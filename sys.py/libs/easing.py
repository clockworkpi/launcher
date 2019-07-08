
import math


def SineIn(t, b, c, d):
	return -c * math.cos(t/d * (math.pi/2)) + c + b

