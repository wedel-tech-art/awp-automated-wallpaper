-- draw_all.lua

-- Global variables
corner_r = 0
bg_colour = 0x000000
bg_alpha = 0.7

require 'cairo'

-- Convert hex color to RGB for Cairo
local function rgb_to_r_g_b(colour, alpha)
  if type(colour) == "string" then
    colour = colour:gsub("#", "") -- Remove # if present
    colour = tonumber(colour, 16) -- Convert hex string to number
  end
  return ((colour / 0x10000) % 0x100) / 255.,
         ((colour / 0x100) % 0x100) / 255.,
         (colour % 0x100) / 255.,
         alpha or 1.0
end

-- Read state file directly from .awp_conky_state.txt
-- Expects: wallpaper_path, workspace_name, logo_path, icon_color, flow, sort, intv, view
local function read_state_file()
  local state = {
    wallpaper_path = "",
    workspace_name = "",
    logo_path = "",
    icon_color = "109daf",
    flow = "",
    sort = "",
    intv = "",
    view = ""
  }
  local file = io.open("/home/ows/awp/conky/.awp_conky_state.txt", "r")
  if not file then
    print("Error: Could not open .awp_conky_state.txt")
    return state
  end
  for line in file:lines() do
    local key, value = line:match("^(.-)=(.+)$")
    if key and value then
      state[key] = value:gsub("^%s*(.-)%s*$", "%1")
    end
  end
  file:close()
  return state
end

-- Parse wallpaper path to get numd, name, extn
local function parse_wallpaper_path(path)
  local numd = "N/A"
  local name = "No wallpaper"
  local extn = "N/A"
  if path and path ~= "" then
    local base = path:match("([^/]+)$") or path
    local separator_pos = base:find("--", 1, true)
    if separator_pos then
      name = base:sub(1, separator_pos - 1)
      local date_part = base:sub(separator_pos + 2)
      numd, extn = date_part:match("^(.-)%.([^%.]+)$")
      if not numd then
        numd = date_part
        extn = "N/A"
      end
    else
      name, extn = base:match("^(.-)%.([^%.]+)$")
      if not name then
        name = base
        extn = "N/A"
      end
    end
  end
  return numd or "N/A", name, extn
end

-- Get wallpaper name (basename) from path
local function get_wallpaper_name(path)
  if path and path ~= "" then
    return path:match("([^/]+)$") or path
  end
  return "No wallpaper"
end

-- Background for lua_draw_hook_pre
function conky_draw_bg()
  if conky_window == nil then return end
  local w, h = conky_window.width, conky_window.height
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, w, h)
  local cr = cairo_create(cs)

  cairo_move_to(cr, corner_r, 0)
  cairo_line_to(cr, w - corner_r, 0)
  cairo_curve_to(cr, w, 0, w, 0, w, corner_r)
  cairo_line_to(cr, w, h - corner_r)
  cairo_curve_to(cr, w, h, w, h, w - corner_r, h)
  cairo_line_to(cr, corner_r, h)
  cairo_curve_to(cr, 0, h, 0, h, 0, h - corner_r)
  cairo_line_to(cr, 0, corner_r)
  cairo_curve_to(cr, 0, 0, 0, 0, corner_r, 0)
  cairo_close_path(cr)

  cairo_set_source_rgba(cr, rgb_to_r_g_b(bg_colour, bg_alpha))
  cairo_fill(cr)

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Logo for lua_draw_hook_post, configurable position
function conky_draw_dynamic_image(x, y)
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local image_path = state.logo_path

  -- Draw logo
  if image_path ~= "" and not image_path:match("Error") then
    local file_exists = io.open(image_path, "r")
    if file_exists then
      file_exists:close()
      local img = cairo_image_surface_create_from_png(image_path)
      local img_w = cairo_image_surface_get_width(img)
      local img_h = cairo_image_surface_get_height(img)
      local target_w, target_h = 26, 26
      local scale_x = target_w / img_w
      local scale_y = target_h / img_h
      cairo_save(cr)
      cairo_translate(cr, x, y)
      cairo_scale(cr, scale_x, scale_y)
      cairo_set_source_surface(cr, img, 0, 0)
      cairo_paint_with_alpha(cr, 1.0)
      cairo_restore(cr)
      cairo_surface_destroy(img)
    else
      print("Error: Logo file not found: " .. image_path)
    end
  end

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Desk info (horizontal) for lua_draw_hook_post
function conky_draw_desk_info()
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local dynamic_color = state.icon_color or "109daf"

  local font = "Source Code Pro"
  local font_size = 11
  local color1 = "ffffff"
  local x_offset = 386
  local line_spacing = font_size + 5
  local text_spacing = 8
  local y_offset_top = 18

  local desk_colr_intv_flow_sort_view = {
    {label="D E S K - ", value=state.workspace_name or "N/A"},
    {label="F L O W - ", value=state.flow or "N/A"},
    {label="C O L R - ", value=state.icon_color or "N/A"},
    {label="S O R T - ", value=state.sort or "N/A"},
    {label="I N T V - ", value=state.intv or "N/A"},
    {label="V I E W - ", value=state.view or "N/A"},
  }

  cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
  cairo_set_font_size(cr, font_size)
  local extents = cairo_text_extents_t:create()

  for i=1,#desk_colr_intv_flow_sort_view,2 do
    -- Left column: DESK, COLR, INTV
    cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
    cairo_move_to(cr, x_offset-55, y_offset_top-2)
    cairo_show_text(cr, desk_colr_intv_flow_sort_view[i].label)
    cairo_text_extents(cr, desk_colr_intv_flow_sort_view[i].label, extents)
    cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
    cairo_move_to(cr, x_offset-55 + extents.width + text_spacing, y_offset_top-2)
    cairo_show_text(cr, desk_colr_intv_flow_sort_view[i].value)
    -- Right column: FLOW, SORT, VIEW
    if desk_colr_intv_flow_sort_view[i+1] then
      cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
      cairo_move_to(cr, x_offset+90, y_offset_top)
      cairo_show_text(cr, desk_colr_intv_flow_sort_view[i+1].label)
      cairo_text_extents(cr, desk_colr_intv_flow_sort_view[i+1].label, extents)
      cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
      cairo_move_to(cr, x_offset+90 + extents.width + text_spacing, y_offset_top)
      cairo_show_text(cr, desk_colr_intv_flow_sort_view[i+1].value)
    end
    y_offset_top = y_offset_top + line_spacing
  end

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Divisory line for lua_draw_hook_post
function conky_draw_divisory_line()
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local dynamic_color = state.icon_color or "109daf"

  local x_offset = 66
  local y_offset_top = 18 + 3 * (11 + 5) - 8 -- After 3 lines of desk_info

  cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
  cairo_set_line_width(cr, 1)
  cairo_move_to(cr, x_offset-65, y_offset_top)
  cairo_line_to(cr, x_offset + 320, y_offset_top)
  cairo_stroke(cr)

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Wallpaper info for lua_draw_hook_post, configurable position
function conky_draw_wallpaper_info(x, y)
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local dynamic_color = state.icon_color or "109daf"
  local numd, name, extn = parse_wallpaper_path(state.wallpaper_path)

  local font = "Source Code Pro"
  local font_size = 11
  local color1 = "ffffff"
  local line_spacing = font_size + 5
  local text_spacing = 8
  local y_offset_bottom = y

  local numd_name_extn = {
    {label="N U M D - ", value=numd},
    {label="N A M E - ", value=name},
    {label="E X T N - ", value=extn},
  }

  cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
  cairo_set_font_size(cr, font_size)
  local extents = cairo_text_extents_t:create()

  for i=1,#numd_name_extn do
    cairo_text_extents(cr, numd_name_extn[i].label, extents)
    local x_label = x
    cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
    cairo_move_to(cr, x_label, y_offset_bottom)
    cairo_show_text(cr, numd_name_extn[i].label)
    local x_value = x + extents.width + text_spacing
    cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
    cairo_move_to(cr, x_value, y_offset_bottom)
    cairo_show_text(cr, numd_name_extn[i].value)
    y_offset_bottom = y_offset_bottom + line_spacing
  end

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Wallpaper name only (horizontal) for lua_draw_hook_post, configurable position
function conky_draw_wallpaper_name(x, y)
  if conky_window == nil then return end
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local dynamic_color = state.icon_color or "109daf"
  local wallpaper_name = get_wallpaper_name(state.wallpaper_path)

  local font = "Source Code Pro"
  local font_size = 11

  cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
  cairo_set_font_size(cr, font_size)
  cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
  cairo_move_to(cr, x, y)
  cairo_show_text(cr, wallpaper_name)

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- Wallpaper name vertical with spaced characters for lua_draw_hook_post, right-aligned
function conky_draw_wallpaper_name_vertical_spaced()
  if conky_window == nil then return end
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)

  -- Read state
  local state = read_state_file()
  local dynamic_color = state.icon_color or "109daf"
  local wallpaper_name = get_wallpaper_name(state.wallpaper_path)

  local font = "Source Code Pro"
  local font_size = 10
  local line_spacing = font_size - 3
  local edge_spacing = 12
  local y_start = edge_spacing

  -- Add spaces between characters (Matrix-style)
  local spaced_name = ""
  for i = 1, #wallpaper_name do
    spaced_name = spaced_name .. wallpaper_name:sub(i, i) .. " "
  end
  spaced_name = spaced_name:sub(1, -2) -- Remove trailing space

  cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
  cairo_set_font_size(cr, font_size)
  cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))

  -- Find widest spaced character for right alignment
  local extents = cairo_text_extents_t:create()
  local max_width = 0
  for i = 1, #spaced_name do
    local char = spaced_name:sub(i, i)
    cairo_text_extents(cr, char, extents)
    if extents.width > max_width then
      max_width = extents.width
    end
  end

  -- Right-align text (12px from right edge)
  local x = conky_window.width - max_width - edge_spacing

  -- Draw each character vertically
  for i = 1, #spaced_name do
    local char = spaced_name:sub(i, i)
    cairo_move_to(cr, x, y_start + (i - 1) * line_spacing)
    cairo_show_text(cr, char)
  end

  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end

-- It's based on the same principles as the bottom bar function.
function conky_draw_sys_info()
    local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
    local cr = cairo_create(cs)

    -- Read state for dynamic color
    local state = read_state_file()
    local dynamic_color = state.icon_color or "109daf"

    local font = "Source Code Pro"
    local font_size = 11
    local color1 = "ffffff"

    -- The y_offset is now relative to the bottom of the Conky window.
    local y_offset = 34

    -- Define the items to display using Conky variables.
    -- We'll use conky_parse to get the real-time values.
    local sys_info_items = {
        {label="M E M R - ", value="${mem}/${memmax}/${memeasyfree}"},
        {label="S W A P - ", value="${swap}/${swapmax}/${swapfree}"},
        {label="S D A 2 - ", value="${fs_used /mnt/windows}/${fs_size /mnt/windows}/${fs_free /mnt/windows}"},
        {label="S D A 3 - ", value="${fs_used /mnt/owstudios}/${fs_size /mnt/owstudios}/${fs_free /mnt/owstudios}"},
        {label="S D A 5 - ", value="${fs_used /mnt/internal1500}/${fs_size /mnt/internal1500}/${fs_free /mnt/internal1500}"},
        {label="S D B 1 - ", value="${fs_used /}/${fs_size /}/${fs_free /}"},
        {label="S D B 3 - ", value="${fs_used /home/ows}/${fs_size /home/ows}/${fs_free /home/ows}"},
        {label="S D C 1 - ", value="${fs_used /mnt/internal2000}/${fs_size /mnt/internal2000}/${fs_free /mnt/internal2000}"},
    }

    cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
    cairo_set_font_size(cr, font_size)
    local extents = cairo_text_extents_t:create()
    local x_offset = 41 -- Starting X position. Adjust as needed.
    local text_spacing = 8 -- Spacing between the label and the value
    local separator_spacing = 37 -- Spacing for the separator

    for i=1,#sys_info_items do
        local item = sys_info_items[i]
        
        -- Get the dynamic value from Conky
        local parsed_value = conky_parse(item.value) or "N/A"

        -- Draw the label
        cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
        cairo_move_to(cr, x_offset, y_offset -5)
        cairo_show_text(cr, item.label)
        cairo_text_extents(cr, item.label, extents)

        -- Draw the value
        cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
        cairo_move_to(cr, x_offset + extents.width + text_spacing, y_offset-5)
        cairo_show_text(cr, parsed_value)
        cairo_text_extents(cr, parsed_value, extents)
        
        -- Move the x_offset for the next item
        x_offset = x_offset + extents.x_advance + text_spacing

        -- Draw the separator if it's not the last item
        if i < #sys_info_items then
            cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
            cairo_move_to(cr, x_offset + 27 + separator_spacing, y_offset-5)
            cairo_show_text(cr, "|")
            x_offset = x_offset + separator_spacing * 2
        end
    end

    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end

-- This is a new function to draw a horizontal bar at the bottom of the screen.
-- It's based on your original conky_draw_desk_info function.
-- You should call this function from your main lua_draw_hook_post function.
function conky_draw_wp_info()
    local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
    local cr = cairo_create(cs)

    -- Read state using the existing function
    local state = read_state_file()
    local dynamic_color = state.icon_color or "109daf"
    local wallpaper_name = get_wallpaper_name(state.wallpaper_path)
    
    -- ← NEW: Get blanking info from state file
    local blanking_timeout = "N/A"
    local blanking_paused = false
    for line in io.lines("/home/ows/awp/conky/.awp_conky_state.txt") do
        if line:match("^blanking_timeout=") then
            blanking_timeout = line:match("^blanking_timeout=(.*)$")
        elseif line:match("^blanking_paused=") then
            blanking_paused = (line:match("^blanking_paused=(.*)$") == "true")
        end
    end
    -- If paused, override timeout display
    if blanking_paused then
        blanking_timeout = "PAUSED"
    end

    local font = "Source Code Pro"
    local font_size = 11
    local color1 = "ffffff"

    -- The y_offset is now relative to the bottom of the Conky window.
    -- Adjust the '20' to move the bar up or down.
    local y_offset = conky_window.height - 28 

    -- Define all 10 items to display in the specified order.
    -- ← BLANKING INFO INSERTED between TIME and WALL
    local wp_info_items = {
        {label="D E S K - ", value=state.workspace_name or "N/A"},
        {label="C O L R - ", value=state.icon_color or "N/A"},
        {label="I N T V - ", value=state.intv or "N/A"},
        {label="F L O W - ", value=state.flow or "N/A"},
        {label="S O R T - ", value=state.sort or "N/A"},
        {label="V I E W - ", value=state.view or "N/A"},
        {label="D A T E - ", value=os.date("%Y.%m.%d")},
        {label="T I M E - ", value=os.date("%H:%M")},
        {label="B L N K - ", value=blanking_timeout},  -- ← NEW: Blanking info
        {label="W A L L - ", value=wallpaper_name or "N/A"},
    }

    cairo_select_font_face(cr, font, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
    cairo_set_font_size(cr, font_size)
    local extents = cairo_text_extents_t:create()
    local x_offset = 41 -- Starting X position. Adjust as needed.
    local text_spacing = 8 -- Spacing between the label and the value
    local separator_spacing = 15 -- Spacing for the separator

    for i=1,#wp_info_items do
        local item = wp_info_items[i]

        -- Draw the label (e.g., "D E S K - ")
        cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
        cairo_move_to(cr, x_offset, y_offset + 5)
        cairo_show_text(cr, item.label)
        cairo_text_extents(cr, item.label, extents)

        -- Draw the value (e.g., "N/A")
        cairo_set_source_rgba(cr, rgb_to_r_g_b(dynamic_color))
        cairo_move_to(cr, x_offset + extents.width + text_spacing, y_offset + 5)
        cairo_show_text(cr, item.value)
        cairo_text_extents(cr, item.value, extents)
        
        -- Move the x_offset for the next item
        x_offset = x_offset + 50 + extents.x_advance + text_spacing

        -- Draw the separator if it's not the last item
        if i < #wp_info_items then
            cairo_set_source_rgba(cr, rgb_to_r_g_b(color1))
            cairo_move_to(cr, x_offset + separator_spacing, y_offset + 5)
            cairo_show_text(cr, "|")
            x_offset = x_offset + separator_spacing * 2
        end
    end

    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end

-- Minimal display (post): logo only, for lua_draw_hook_post
function conky_draw_minimal_post()
  if conky_window == nil then return end
  conky_draw_dynamic_image(275, 60)
end

-- Info-only display (post): desk info (horizontal) and wallpaper info, for lua_draw_hook_post
function conky_draw_info_only_post()
  if conky_window == nil then return end
  conky_draw_desk_info()
  conky_draw_wallpaper_info(11, 18 + 3 * (11 + 5) + 9)
end

-- Name-only display (post): logo and wallpaper name (horizontal), for lua_draw_hook_post
function conky_draw_name_only_post()
  if conky_window == nil then return end
  conky_draw_dynamic_image(8, 8)
  conky_draw_wallpaper_name(62, 80)
end

-- All content: logo, desk info (horizontal), divisory line, wallpaper info, and wallpaper name
function conky_draw_content()
  if conky_window == nil then return end
  conky_draw_dynamic_image(8, 8)
  conky_draw_desk_info()
  --conky_draw_divisory_line()
  conky_draw_wallpaper_info(62, -39 + 3 * (11 + 5) + 9)
end

-- Full display: background and all content
function conky_draw_all()
  if conky_window == nil then return end
  conky_draw_bg()
  conky_draw_content()
end

function conky_draw_wp_sys_info()
  if conky_window == nil then return end
  conky_draw_wp_info()
  conky_draw_sys_info()
  conky_draw_dynamic_image(9, 5)
end
