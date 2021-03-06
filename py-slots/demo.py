#!/usr/bin/python
"""
demo.py
"""

import dis
import os
import subprocess
import sys
import timeit
import time


class Point(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y


# Are slots like a struct?
class PointSlots(object):
  __slots__ = ('x', 'y')

  def __init__(self, x, y):
    self.x = x
    self.y = y


def Compute(points):
  total = 0
  # Test attribute access speed
  for p in points:
    total += p.x 
    total += p.y
  return total


class LPoint(object):
  def __init__(self, x, y):
    self.x01234567890123456789 = x
    self.y01234567890123456789 = y


def LCompute(points):
  total = 0
  # Test attribute access speed
  for p in points:
    total += p.x01234567890123456789
    total += p.y01234567890123456789
  return total


def ComputeList(intlist, n):
  total = 0
  for i in xrange(0, n*2, 2):
    total += intlist[i]
    total += intlist[i+1]
  return total


def ComputeFlatList(intlist, n):
  """
  NOTE: Does NOT do intlist[i] at all.
  """
  total = 0
  for i in intlist:
    total += i
  return total


# Are slots like a struct?
class LPointSlots(object):
  __slots__ = ('x01234567890123456789', 'y01234567890123456789')

  def __init__(self, x, y):
    self.x01234567890123456789 = x
    self.y01234567890123456789 = y


def main(argv):
  #p = Point(5, 10)
  #ps = PointSlots(5, 10)
  #p.z = 99
  #ps.z = 99  # not allowed

  if argv[1] == 'dis':
    dis.dis(Compute)
    return

  if argv[1] == 'dis2':
    def FunctionUsingModule(paths):
      for p in paths:  # multiple LOAD_ATTR in a loop.
        print os.path.exists(p)
    dis.dis(FunctionUsingModule)
    return

  class_name = argv[1]
  n = int(argv[2])

  # Do List Comparison.  It's a little faster at ~67 ms vs ~83 for Point and
  # ~73 for PointSlots.  Not overwhelmingly faster though.
  # So there are bigger overheads than the name to number issue?

  if class_name == '<list>':
    intlist = range(n * 2)
    start_time = time.time()
    total = ComputeList(intlist, n)
    elapsed = time.time() - start_time
    print 'Computed %d from %d points in %.1f ms' % (total, n, elapsed * 1000)
    return

  if class_name == '<flatlist>':  # ~49 ms on 1M entries
    intlist = range(n * 2)
    start_time = time.time()
    total = ComputeFlatList(intlist, n)
    elapsed = time.time() - start_time
    print 'Computed %d from %d points in %.1f ms' % (total, n, elapsed * 1000)
    return

  # ~13 ms on 1M entries.  So interpreter loop overhead dominates attribute
  # access in this case!
  if class_name == '<sum_c>':
    intlist = range(n * 2)
    start_time = time.time()
    total = sum(intlist)
    elapsed = time.time() - start_time
    print 'Computed %d from %d points in %.1f ms' % (total, n, elapsed * 1000)
    return

  if class_name == 'Point':
    cls = Point
    compute_func = Compute
  elif class_name == 'PointSlots':
    cls = PointSlots
    compute_func = Compute
  elif class_name == 'LPoint':
    cls = LPoint
    compute_func = LCompute
  elif class_name == 'LPointSlots':
    cls = LPointSlots
    compute_func = LCompute
  else:
    raise AssertionError

  print 'Creating %d %s instances...' % (n, class_name)
  points = []
  for i in xrange(n):
    o = cls(i, i)
    points.append(o)

  start_time = time.time()
  total = compute_func(points)
  elapsed = time.time() - start_time
  print 'Computed %d from %d points in %.1f ms' % (total, n, elapsed * 1000)

  # Both 64?  getsizeof() isn't recursive
  #print sys.getsizeof(p)
  #print sys.getsizeof(ps)

  if os.getenv('SHOW_MEM'):
    pat = '^VmPeak'
    argv = ['grep', pat, '/proc/%d/status' % os.getpid()]
    subprocess.call(argv)


if __name__ == '__main__':
  try:
    main(sys.argv)
  except RuntimeError as e:
    print >>sys.stderr, 'FATAL: %s' % e
    sys.exit(1)
