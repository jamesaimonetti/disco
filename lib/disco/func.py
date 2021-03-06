"""
:mod:`disco.func` --- Functions for constructing Disco jobs
===========================================================

A Disco job is specified by one or more user-defined :term:`job
functions`, namely *map*, *reduce*, *combiner* and *partitioner* functions
(see :class:`disco.core.JobDict` for more information).
Of these functions, only *map* is required.

.. hint::
   When writing custom functions, take into account the following
   features of the disco worker environment:

        - Only the specified function is included in the request.
          The function can't refer to anything outside of its local scope.
          It can't call any functions specified elsewhere in your source file.
          Nor can it refer to any global names, including any imported modules.
          If you need to use a module, import it within the function body.

          In short, job functions must be :term:`pure <pure function>`.

        - The function should not print anything to stderr.
          The task uses stderr to signal events to the master.
          You can raise a :class:`disco.error.DataError`,
          to abort the task on this node and try again on another node.
          It is usually a best to let the task fail if any exceptions occur:
          do not catch any exceptions from which you can't recover.
          When exceptions occur, the disco worker will catch them and
          signal an appropriate event to the master.

User-defined Functions
----------------------

The following types of functions can be provided by the user:

.. autofunction:: map
.. autofunction:: partition
.. autofunction:: combiner
.. autofunction:: reduce
.. autofunction:: init
.. autofunction:: input_stream
.. autofunction:: output_stream


Interfaces
----------

.. autoclass:: InputStream
    :members: __iter__, read
.. autoclass:: OutputStream
    :members: 

Default/Utility Functions
-------------------------

These functions are provided by Disco to help :class:`disco.core.Job` creation:

.. autofunction:: default_partition
.. autofunction:: make_range_partition
.. autofunction:: nop_reduce
.. autofunction:: map_line_reader
.. autofunction:: chain_reader
.. autofunction:: netstr_reader
.. autofunction:: netstr_writer
.. autofunction:: object_reader
.. autofunction:: object_writer
.. autofunction:: re_reader
.. autofunction:: map_input_stream
.. autofunction:: map_output_stream
.. autofunction:: reduce_input_stream
.. autofunction:: reduce_output_stream
"""
import re, cPickle
from disco.error import DataError

def map(entry, params):
    """
    Returns an iterable of (key, value) pairs given an *entry*.

    :param entry:  entry from the input stream
    :type params:  :class:`disco.core.Params`
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.
                   Used to maintain state between calls to the map function.

    For instance::

        def fun_map(e, params):
            return [(w, 1) for w in e.split()]

    This example takes a line of text as input in *e*, tokenizes it,
    and returns a list of words as the output.

    The map task can also be an external program.
    For more information, see :ref:`discoext`.
    """

def partition(key, nr_partitions, params):
    """
    Returns an integer in ``range(0, nr_partitions)``.

    :param key: is a key object emitted by a task function
    :param nr_partitions: the number of partitions
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.

    """

def combiner(key, value, buffer, done, params):
    """
    Returns an iterator of ``(key, value)`` pairs or ``None``.

    :param key: key object emitted by the :func:`map`
    :param value: value object emitted by the :func:`map`
    :param buffer: an accumulator object (a dictionary),
                   that combiner can use to save its state.
                   The function must control the *buffer* size,
                   to prevent it from consuming too much memory, by calling
                   ``buffer.clear()`` after each block of results.
    :param done: flag indicating if this is the last call with a given *buffer*
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.

    This function receives all output from the
    :func:`disco.func.map` before it is saved to intermediate results.
    Only the output produced by this function is saved to the results.

    After :func:`disco.func.map` has consumed all input entries,
    combiner is called for the last time with the *done* flag set to ``True``.
    This is the last opportunity for the combiner to return something.
    """

def reduce(input_stream, output_stream, params):
    """
    Takes three parameters, and adds reduced output to an output object.

    :param input_stream: :class:`disco.func.InputStream` object that is used
        to iterate through input entries.
    :param output_stream: :class:`disco.func.InputStream` object that is used
        to output results.
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.

    For instance::

        def fun_reduce(iter, out, params):
            d = {}
            for w, c in iter:
                d[w] = d.get(w, 1) + 1
            for w, c in d.iteritems():
                out.add(w, c)

    This example counts how many teams each key appears.

    The reduce task can also be an external program.
    For more information, see :ref:`discoext`.
    """

def init(input_iter, params):
    """
    Perform some task initialization.

    :param input_iter: an iterator returned by a :func:`reader`
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.

    Typically this function is used to initialize some modules in the worker
    environment (e.g. ``ctypes.cdll.LoadLibrary()``), to initialize some
    values in *params*, or to skip unneeded entries in the beginning
    of the input stream.
    """

def input_stream(stream, size, url, params):
    """
    :param stream: :class:`disco.func.InputStream` object
    :param size: size of the input (may be ``None``)
    :param url: url of the input

    Returns a triplet (:class:`disco.func.InputStream`, size, url) that is
    passed to the next *input_stream* function in the chain. The
    last :class:`disco.func.InputStream` object returned by the chain is used
    to iterate through input entries.

    Using an :func:`disco.func.input_stream` allows you to customize
    how input urls are opened.
    """

def output_stream(stream, partition, url, params):
    """
    :param stream: :class:`disco.func.OutputStream` object
    :param partition: partition id
    :param url: url of the input
    :param params: the :class:`disco.core.Params` object specified
                   by the *params* parameter in :class:`disco.core.JobDict`.
    
    Returns a triplet (:class:`disco.func.OutputStream`, size, url) that is
    passed to the next *output_stream* function in the chain. The
    :meth:`disco.func.OutputStream.add` method of the last
    :class:`disco.func.OutputStream` object returned by the chain is used
    to output entries from map or reduce.

    Using an :func:`output_stream` allows you to customize where and how
    output is stored. The default should almost always be used.
    """

class OutputStream:
    """
    A file-like object returned by the ``map_output_stream`` or 
    ``reduce_output_stream`` chain of :func:`disco.func.output_stream` functions.
    Used to encode key, value pairs add write them to the underlying file object.
    """
    def write(data):
        """
        Writes serialized key, value pairs to the underlying file object.
        """

    def add(key, value):
        """
        Adds a key, value pair to the output stream. This method typically
        calls *self.write()* to write a serialized pair to the actual 
        file object.
        """

class InputStream:
    """
    A file-like object returned by the ``map_input_stream`` or 
    ``reduce_input_stream`` chain of :func:`disco.func.input_stream` functions.
    Used either to read bytes from the input source or to iterate through input
    entries.
    """
    def __iter__():
        """
        Iterates through input entries. Typically calls *self.read()* to read
        bytes from the underlying file object, which are deserialized to the
        actual input entries.
        """
    
    def read(num_bytes=None):
        """
        Reads at most *num_bytes* from the input source, or until EOF if *num_bytes*
        is not specified.
        """

def old_netstr_reader(fd, size, fname, head = ''):
    """
    Reader for Disco's default/internal key-value format.

    Reads output of a map / reduce job as the input for a new job.
    Specify this function as your :func:`map_reader`
    to use the output of a previous job as input to another job.
    :func:`chain_reader` is an alias for :func:`netstr_reader`.
    """
    if size == None:
        err("Content-length must be defined for netstr_reader")
    def read_netstr(idx, data, tot):
        ldata = len(data)
        i = 0
        lenstr = ""
        if ldata - idx < 11:
            data = data[idx:] + fd.read(8192)
            ldata = len(data)
            idx = 0

        i = data.find(" ", idx, idx + 11)
        if i == -1:
            raise DataError("Corrupted input: "\
                            "Could not parse a value length at %d bytes."\
                            % (tot), fname)
        else:
            lenstr = data[idx:i + 1]
            idx = i + 1

        if ldata < i + 1:
            raise DataError("Truncated input: "\
                            "Expected %d bytes, got %d" % (size, tot), fname)

        try:
            llen = int(lenstr)
        except ValueError:
            raise DataError("Corrupted input: "\
                            "Could not parse a value length at %d bytes."\
                            % (tot), fname)

        tot += len(lenstr)

        if ldata - idx < llen + 1:
            data = data[idx:] + fd.read(llen + 8193)
            ldata = len(data)
            idx = 0

        msg = data[idx:idx + llen]

        if idx + llen + 1 > ldata:
            raise DataError("Truncated input: "\
                            "Expected a value of %d bytes (offset %u bytes)"\
                            % (llen + 1, tot), fname)

        tot += llen + 1
        idx += llen + 1
        return idx, data, tot, msg

    data = head + fd.read(8192)
    tot = idx = 0
    while tot < size:
        key = val = ""
        idx, data, tot, key = read_netstr(idx, data, tot)
        idx, data, tot, val = read_netstr(idx, data, tot)
        yield key, val

def re_reader(item_re_str, fd, size, fname, output_tail=False, read_buffer_size=8192):
    """
    A map reader that uses an arbitrary regular expression to parse the input
    stream.

    :param item_re_str: regular expression for matching input items

    The reader works as follows:

     1. X bytes is read from *fd* and appended to an internal buffer *buf*.
     2. ``m = regexp.match(buf)`` is executed.
     3. If *buf* produces a match, ``m.groups()`` is yielded, which contains an
        input entry for the map function. Step 2. is executed for the remaining
        part of *buf*. If no match is made, go to step 1.
     4. If *fd* is exhausted before *size* bytes have been read,
        and *size* tests ``True``,
        a :class:`disco.error.DataError` is raised.
     5. When *fd* is exhausted but *buf* contains unmatched bytes, two modes are
        available: If ``output_tail=True``, the remaining *buf* is yielded as is.
        Otherwise, a message is sent that warns about trailing bytes.
        The remaining *buf* is discarded.

    Note that :func:`re_reader` fails if the input streams contains unmatched
    bytes between matched entries.
    Make sure that your *item_re_str* is constructed so that it covers all
    bytes in the input stream.

    :func:`re_reader` provides an easy way to construct parsers for textual
    input streams.
    For instance, the following reader produces full HTML
    documents as input entries::

        def html_reader(fd, size, fname):
            for x in re_reader("<HTML>(.*?)</HTML>", fd, size, fname):
                yield x[0]

    Note that since ``output_tail=True`` in :func:`map_line_reader`, an input
    file that lacks the final newline character is silently accepted.
    """
    item_re = re.compile(item_re_str)
    buf = ""
    tot = 0
    while True:
        if size:
            r = fd.read(min(read_buffer_size, size - tot))
        else:
            r = fd.read(read_buffer_size)
        tot += len(r)
        buf += r

        m = item_re.match(buf)
        while m:
            yield m.groups()
            buf = buf[m.end():]
            m = item_re.match(buf)

        if not len(r) or (size!=None and tot >= size):
            if size != None and tot < size:
                raise DataError("Truncated input: "\
                "Expected %d bytes, got %d" % (size, tot), fname)
            if len(buf):
                if output_tail:
                    yield [buf]
                else:
                    print "Couldn't match the last %d bytes in %s. "\
                    "Some bytes may be missing from input." % (len(buf), fname)
            break


def default_partition(key, nr_partitions, params):
    """Returns ``hash(str(key)) % nr_partitions``."""
    return hash(str(key)) % nr_partitions


def make_range_partition(min_val, max_val):
    """
    Returns a new partitioning function that partitions keys in the range
    *[min_val:max_val]* into equal sized partitions.

    The number of partitions is defined by *partitions*
    in :class:`disco.core.JobDict`.
    """
    r = max_val - min_val
    f = "lambda k, n, p: int(round(float(int(k) - %d) / %d * (n - 1)))" %\
        (min_val, r)
    return eval(f)


def noop(*args, **kwargs):
    pass

def nop_reduce(iter, out, params):
    """
    No-op reduce.

    This function can be used to combine results per partition from many
    map functions to a single result file per partition.
    """
    for k, v in iter:
        out.add(k, v)

def map_line_reader(fd, sze, fname):
    """Yields each line of input."""
    for x in re_reader("(.*?)\n", fd, sze, fname, output_tail = True):
        yield x[0]

def netstr_writer(fd, key, value, params):
    """Writer for Disco's default/internal key-value format."""
    skey = str(key)
    sval = str(value)
    fd.write("%d %s %d %s\n" % (len(skey), skey, len(sval), sval))

def object_writer(fd, key, value, params):
    """
    *(Deprecated in 0.3)*
    A wrapper for :func:`netstr_writer` that uses Python's ``cPickle``
    module to deserialize strings to Python objects.
   """
    skey = cPickle.dumps(key, cPickle.HIGHEST_PROTOCOL)
    sval = cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)
    fd.write("%d %s %d %s\n" % (len(skey), skey, len(sval), sval))

def object_reader(fd, sze, fname):
    """
    *(Deprecated in 0.3)*
    A wrapper for :func:`netstr_reader` that uses Python's ``cPickle``
    module to serialize arbitrary Python objects to strings.
    """
    print"NOTE! Object_reader and object_writer are deprecated. "\
         "Python objects are now serialized by default."
    for k, v in netstr_reader(fd, sze, fname):
        yield (cPickle.loads(k), cPickle.loads(v))

def map_input_stream(stream, size, url, params):
    """
    An :func:`input_stream` which looks at the scheme of ``url``
    and tries to import a function named ``input_stream``
    from the module ``disco.schemes.scheme_SCHEME``,
    where SCHEME is the parsed scheme.
    If no scheme is found in the url, ``file`` is used.
    The resulting input stream is then used.
    """
    m = re.match('(\w+)://', url)
    scheme = m.group(1) if m else 'file'
    mod = __import__('disco.schemes.scheme_%s' % scheme,
                     fromlist=['scheme_%s' % scheme])
    Task.insert_globals([mod.input_stream])
    return mod.input_stream(stream, size, url, params)

reduce_input_stream = map_input_stream

def string_input_stream(string, size, url, params):
    from cStringIO import StringIO
    return StringIO(string), len(string), url

def map_output_stream(stream, partition, url, params):
    """
    An :func:`output_stream` which returns a handle to a partition output.
    The handle ensures that if a task fails, partially written data is ignored.
    """
    from disco.fileutils import AtomicFile, PartitionFile
    mpath, murl = Task.map_output(partition)
    if not Task.ispartitioned:
        Task.add_blob(mpath)
        return AtomicFile(mpath, 'w'), murl
    else:
        ppath, purl = Task.partition_output(partition)
        Task.add_blob(ppath)
        return PartitionFile(ppath, mpath, 'w'), purl

def reduce_output_stream(stream, partition, url, params):
    """
    An :func:`output_stream` which returns a handle to a reduce output.
    The handle ensures that if a task fails, partially written data is ignored.
    """
    from disco.fileutils import AtomicFile
    path, url = Task.reduce_output()
    Task.add_blob(path)
    return AtomicFile(path, 'w'), url

# backwards compatibility for readers and writers
# remove when readers and writers are gone

def reader_wrapper(reader):
    from util import argcount
    if argcount(reader) == 3:
        # old style reader without params
        def reader_input_stream(stream, size, url, params):
            return reader(stream, size, url)
        return reader_input_stream
    else:
        return reader

def writer_wrapper(writer):
    def writer_output_stream(stream, partition, url, params):
        stream.add = lambda k, v: writer(stream, k, v, params)
        return stream, url
    return writer_output_stream

def disco_output_stream(stream, partition, url, params, version = -1,
                        compress_level = 2, min_chunk = 1 * 1024**2):
    from disco.fileutils import DiscoOutput
    return DiscoOutput(stream,
                       version = version,
                       compress_level = compress_level,
                       min_chunk = min_chunk), url

def disco_input_stream(stream, size, url, ignore_corrupt = False):
    import struct, cStringIO, gzip, cPickle, zlib
    offset = 0
    while True:
        header = stream.read(1)
        if not header:
            return
        if ord(header[0]) < 128:
            for e in old_netstr_reader(stream, size, url, header):
                yield e
            return
        try:
            is_compressed, checksum, chunk_size =\
                struct.unpack('<BIQ', stream.read(13))
        except:
            raise DataError("Truncated data at %d bytes" % offset, url)
        if not chunk_size:
            return
        chunk = stream.read(chunk_size)
        data = ''
        try:
            data = zlib.decompress(chunk) if is_compressed else chunk
            if checksum != (zlib.crc32(data) & 0xFFFFFFFF):
                raise ValueError("Checksum does not match")
        except (ValueError, zlib.error), e:
            if not ignore_corrupt:
                raise DataError("Corrupted data between bytes %d-%d: %s" %
                                (offset, offset + chunk_size, e), url)
        offset += chunk_size
        chunk = cStringIO.StringIO(data)
        while True:
            try:
                yield cPickle.load(chunk)
            except EOFError:
                break

chain_reader = netstr_reader = disco_input_stream
