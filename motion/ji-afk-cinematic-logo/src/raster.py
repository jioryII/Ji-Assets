"""Render real SVG using system librsvg + Cairo (no browser or generated imagery)."""
import ctypes as C
from ctypes.util import find_library
from PIL import Image

rsvg=C.CDLL(find_library('rsvg-2'))
cairo=C.CDLL(find_library('cairo'))
gobj=C.CDLL(find_library('gobject-2.0'))

class Rect(C.Structure):
    _fields_=[('x',C.c_double),('y',C.c_double),('width',C.c_double),('height',C.c_double)]

rsvg.rsvg_handle_new_from_data.argtypes=[C.c_char_p,C.c_size_t,C.c_void_p]
rsvg.rsvg_handle_new_from_data.restype=C.c_void_p
rsvg.rsvg_handle_render_document.argtypes=[C.c_void_p,C.c_void_p,C.POINTER(Rect),C.c_void_p]
rsvg.rsvg_handle_render_document.restype=C.c_int
cairo.cairo_image_surface_create.argtypes=[C.c_int,C.c_int,C.c_int]
cairo.cairo_image_surface_create.restype=C.c_void_p
cairo.cairo_create.argtypes=[C.c_void_p]
cairo.cairo_create.restype=C.c_void_p
cairo.cairo_surface_flush.argtypes=[C.c_void_p]
cairo.cairo_image_surface_get_data.argtypes=[C.c_void_p]
cairo.cairo_image_surface_get_data.restype=C.c_void_p
cairo.cairo_image_surface_get_stride.argtypes=[C.c_void_p]
cairo.cairo_image_surface_get_stride.restype=C.c_int
cairo.cairo_destroy.argtypes=[C.c_void_p]
cairo.cairo_surface_destroy.argtypes=[C.c_void_p]
gobj.g_object_unref.argtypes=[C.c_void_p]

def render_svg(svg, width=1080, height=None):
    height=height or width
    data=svg.encode()
    handle=rsvg.rsvg_handle_new_from_data(data,len(data),None)
    if not handle: raise RuntimeError('Invalid SVG document')
    surface=cairo.cairo_image_surface_create(0,width,height)
    ctx=cairo.cairo_create(surface)
    try:
        if not rsvg.rsvg_handle_render_document(handle,ctx,C.byref(Rect(0,0,width,height)),None):
            raise RuntimeError('librsvg failed to render')
        cairo.cairo_surface_flush(surface)
        stride=cairo.cairo_image_surface_get_stride(surface)
        raw=C.string_at(cairo.cairo_image_surface_get_data(surface),stride*height)
        return Image.frombytes('RGBA',(width,height),raw,'raw','BGRA',stride).convert('RGB')
    finally:
        cairo.cairo_destroy(ctx)
        cairo.cairo_surface_destroy(surface)
        gobj.g_object_unref(handle)
