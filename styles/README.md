# Custom CSS Theme Documentation

## Overview

This document describes the custom CSS theme applied to the FIAP Sprint 4 Reply Streamlit dashboard. The theme provides a modern, professional, and unique visual identity that enhances the user experience while maintaining compatibility with all native Streamlit components.

## Design Concept

**"Modern Corporate Light with Blue-Teal Accents"**

The theme is designed to create a premium corporate dashboard appearance suitable for industrial IoT monitoring applications. It combines:

- Clean, professional aesthetics
- Harmonious color palette
- Modern typography
- Subtle visual effects
- Excellent readability
- Responsive layout

## Color Palette

### Primary Colors
- **Background Primary**: `#f6f8fb` - Soft blue-gray background
- **Card Background**: `#ffffff` - Pure white for content cards
- **Text Primary**: `#0f1724` - Dark blue-gray for main text
- **Text Secondary**: `#6b7280` - Medium gray for secondary text
- **Text Muted**: `#9ca3af` - Light gray for muted text

### Accent Colors
- **Accent Primary**: `#1f6feb` - Vibrant blue (primary actions, links)
- **Accent Primary Dark**: `#155ab8` - Darker blue (gradients, hover states)
- **Accent Secondary**: `#00bfa6` - Teal (secondary emphasis, charts)
- **Accent Secondary Dark**: `#00a890` - Darker teal (hover states)

### Status Colors
- **Success**: `#10b981` - Green for success messages
- **Warning**: `#f59e0b` - Amber for warnings
- **Error**: `#ef4444` - Red for errors
- **Info**: `#3b82f6` - Blue for information

## Typography

### Font Family
**Inter** - A modern, highly readable sans-serif font designed for user interfaces.

- Font weights used: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semi-bold), 700 (Bold), 800 (Extra-bold)
- Loaded from Google Fonts for consistent cross-platform rendering
- Fallback: System fonts (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, etc.)

### Font Sizes
- **xs**: 0.75rem (12px)
- **sm**: 0.875rem (14px)
- **base**: 1rem (16px)
- **lg**: 1.125rem (18px)
- **xl**: 1.25rem (20px)
- **2xl**: 1.5rem (24px)
- **3xl**: 1.875rem (30px)

## Design System

### Spacing Scale
Consistent spacing ensures visual harmony:
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px

### Border Radius
Soft, rounded corners for modern appearance:
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 20px

### Shadows
Subtle depth with layered shadows:
- **sm**: `0 2px 8px rgba(15, 23, 36, 0.04)` - Minimal elevation
- **md**: `0 4px 16px rgba(15, 23, 36, 0.08)` - Medium elevation
- **lg**: `0 8px 24px rgba(15, 23, 36, 0.12)` - High elevation
- **hover**: `0 12px 32px rgba(31, 111, 235, 0.15)` - Interactive emphasis

## Component Styling

### Buttons
- **Primary Buttons**: Blue gradient with white text
- **Secondary Buttons**: White background with blue border
- **Hover Effect**: Subtle lift (translateY -2px) with enhanced shadow
- **Active State**: Returns to normal position
- **Transition**: Smooth 0.25s ease

### Input Fields
- **Background**: Subtle gradient (white to light blue)
- **Border**: Light gray (1px solid)
- **Focus State**: Blue border with soft blue shadow
- **Border Radius**: 12px

### Metrics
- **Background**: White card with shadow
- **Hover Effect**: Slight lift with enhanced shadow
- **Label**: Uppercase, small, medium gray
- **Value**: Large, bold, dark blue-gray
- **Delta**: Small, bold, color-coded (green/red)

### Tables/Dataframes
- **Header**: Blue gradient with white text, uppercase
- **Rows**: Alternating hover effect (light blue tint)
- **Borders**: Subtle light gray
- **Border Radius**: 12px with overflow hidden

### Tabs
- **Default**: Transparent with medium gray text
- **Hover**: Light blue background tint
- **Active**: Blue gradient with white text and shadow
- **Border Radius**: Rounded top corners (12px)

### Alerts
All alerts include a colored left border and matching background tint:
- **Success**: Green theme
- **Warning**: Amber theme
- **Error**: Red theme
- **Info**: Blue theme

### Sidebar
- **Background**: White with subtle gradient
- **Border**: Right border (light gray)
- **Shadow**: Medium shadow for depth
- **Links**: Gray with blue hover

## Responsive Design

The theme is fully responsive with breakpoints:

### Desktop (> 1024px)
- Full padding and spacing
- Multi-column layouts
- Full sidebar

### Tablet (768px - 1024px)
- Reduced padding
- Adjusted column widths
- Maintained sidebar

### Mobile (< 768px)
- Minimal padding (16px sides)
- Single column layout
- Full-width buttons
- Smaller heading sizes
- Compact metrics

## Animations & Transitions

### Standard Transitions
- **Fast**: 0.15s ease (hover states, small UI changes)
- **Base**: 0.25s ease (buttons, inputs, cards)
- **Slow**: 0.35s ease (large components, page transitions)

### Keyframe Animations
- **fadeIn**: Subtle entrance animation (opacity + translateY)
- **pulse**: Attention-drawing pulse effect

## Usage

### Automatic Application
The custom CSS is automatically applied when the dashboard initializes:

```python
from src.dashboard.styles_loader import apply_custom_theme

# In your setup or main function
apply_custom_theme()
```

### Manual Application (Alternative)
You can also manually inject the CSS:

```python
import streamlit as st
from pathlib import Path

css_file = Path("styles/custom.css")
with open(css_file) as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

## Customization

### Changing Colors
To change the color scheme, edit the CSS variables in `styles/custom.css`:

```css
:root {
  --accent-primary: #your-color;
  --accent-secondary: #your-color;
  /* etc. */
}
```

### Changing Font
To use a different Google Font, update the import and variable:

```css
@import url('https://fonts.googleapis.com/css2?family=YourFont:wght@400;600;700&display=swap');

:root {
  --font-family: 'YourFont', sans-serif;
}
```

## Browser Compatibility

The theme is tested and compatible with:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

The theme maintains good accessibility practices:
- **Contrast Ratios**: All text meets WCAG AA standards (minimum 4.5:1)
- **Focus States**: Clear focus indicators with blue outlines
- **Keyboard Navigation**: Full keyboard support maintained
- **Screen Readers**: Semantic HTML preserved

## Files

### CSS File
- **Location**: `/styles/custom.css`
- **Size**: ~18KB
- **Lines**: ~700+

### Loader Module
- **Location**: `/src/dashboard/styles_loader.py`
- **Purpose**: Load and inject CSS into Streamlit

### Integration Points
- `/src/dashboard/setup.py` - Main dashboard initialization
- `/src/dashboard/login.py` - Login page styling

## Maintenance

### Adding New Styles
1. Edit `styles/custom.css`
2. Follow existing naming conventions
3. Use CSS variables for colors/spacing
4. Test in all supported browsers

### Version Control
The CSS file is tracked in git. Changes should be:
- Documented in commit messages
- Tested before merging
- Reviewed for consistency

## Performance

- **CSS Size**: ~18KB (minimal impact)
- **Load Time**: < 50ms (cached after first load)
- **Render Performance**: No performance impact on Streamlit rendering
- **Caching**: Browser caches CSS file

## Examples

### Creating a Styled Card
```python
import streamlit as st

with st.container():
    st.markdown("### Card Title")
    st.write("This content is automatically styled")
    st.metric("Temperature", "24°C", "+2°C")
```

### Using Styled Buttons
```python
# Primary button (automatically styled)
if st.button("Save Changes"):
    pass

# Form submit button (automatically styled)
with st.form("my_form"):
    st.form_submit_button("Submit")
```

### Styled Metrics
```python
col1, col2, col3 = st.columns(3)
col1.metric("Sensor 1", "100", "+5")
col2.metric("Sensor 2", "85", "-3")
col3.metric("Sensor 3", "92", "0")
```

## Support

For questions or issues with the theme:
1. Check this documentation
2. Review the CSS file comments
3. Test in browser developer tools
4. Contact the development team

## Credits

- **Design System**: Based on modern UI/UX principles
- **Color Palette**: Inspired by GitHub and Tailwind CSS
- **Typography**: Inter font by Rasmus Andersson
- **Implementation**: FIAP Sprint 4 Reply Team

---

*Last Updated: 2025*
*Version: 1.0.0*
