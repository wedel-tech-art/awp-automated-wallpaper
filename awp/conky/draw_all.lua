require 'cairo'

local function rgb_to_r_g_b(colour, alpha)
    return ((colour / 0x10000) % 0x100) / 255.,
           ((colour / 0x100) % 0x100) / 255.,
           (colour % 0x100) / 255.,
           alpha or 1.0
end

-- 1. The Background function (Transparency)
function conky_draw_bg()
    if conky_window == nil then return end
    local w, h = conky_window.width, conky_window.height
    local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, w, h)
    local cr = cairo_create(cs)
    
    local r = 15 
    cairo_move_to(cr, r, 0)
    cairo_line_to(cr, w-r, 0)
    cairo_curve_to(cr, w, 0, w, 0, w, r)
    cairo_line_to(cr, w, h-r)
    cairo_curve_to(cr, w, h, w, h, w-r, h)
    cairo_line_to(cr, r, h)
    cairo_curve_to(cr, 0, h, 0, h, 0, h - r)
    cairo_line_to(cr, 0, r)
    cairo_curve_to(cr, 0, 0, 0, 0, r, 0)
    cairo_close_path(cr)

    cairo_set_source_rgba(cr, rgb_to_r_g_b(0x000000, 0.5))
    cairo_fill(cr)
    
    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end

function conky_draw_logo(x, y, size, cr)
    local image_path = "../debian.png" 
    local img = cairo_image_surface_create_from_png(image_path)
    
    if cairo_surface_status(img) == CAIRO_STATUS_SUCCESS then
        local img_w = cairo_image_surface_get_width(img)
        local scale = size / img_w
        cairo_save(cr)
        cairo_translate(cr, x, y)
        cairo_scale(cr, scale, scale)
        cairo_set_source_surface(cr, img, 0, 0)
        cairo_paint(cr)
        cairo_restore(cr)
        cairo_surface_destroy(img)
    else
        print("AWP Notice: Demo logo not found at " .. image_path)
    end
end

function conky_render_logo_top()
    if conky_window == nil then return end
    local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
    local cr = cairo_create(cs)
    
    -- Now we call your logo function with the specific settings
    -- Coordinates x=10, y=10 and size=30
    conky_draw_logo(4, 74, 30, cr)
    
    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end
