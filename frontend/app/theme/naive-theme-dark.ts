import type { GlobalThemeOverrides } from 'naive-ui';

export const naiveThemeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily: '"Inter", sans-serif',
    primaryColor: ACCENT,
    primaryColorHover: ACCENT_LIGHT,
    primaryColorPressed: ACCENT_DARK,
    textColorBase: WHITE,
    textColor2: GRAY,
    bodyColor: DARK,
    cardColor: LIGHT_DARK,
    dividerColor: LIGHT,
    borderRadius: '4px',
  },
  Card: {
    color: BG,
    borderColor: LIGHT_DARK,
    textColor: WHITE,
    titleTextColor: GRAY,
    colorModal: MEDIUM,
    borderColorModal: LIGHT,
    borderRadius: '12px',
    titleFontWeight: '400',
    titleFontSizeMedium: '12px',
  },
  Input: {
    color: LIGHT_DARK,
    colorFocus: LIGHT_DARK,
    textColor: WHITE,
    border: `2px solid ${MEDIUM}`,
    borderHover: `2px solid ${ACCENT}`,
    borderFocus: `2px solid ${ACCENT}`,
    placeholderColor: GRAY,

    colorError: LIGHT_DARK,
    colorFocusError: LIGHT_DARK,
    textColorError: WHITE,
    borderError: `2px solid ${RED}`,
    borderHoverError: `2px solid ${RED_SOFT}`,
    borderFocusError: `2px solid ${RED}`,
    caretColorError: RED,

    colorWarning: LIGHT_DARK,
    colorFocusWarning: LIGHT_DARK,
    textColorWarning: WHITE,
    borderWarning: `2px solid ${YELLOW}`,
    borderHoverWarning: `2px solid ${YELLOW_SOFT}`,
    borderFocusWarning: `2px solid ${YELLOW}`,
    caretColorWarning: YELLOW,
  },
  Form: {
    labelTextColor: GRAY,
  },
  Button: {
    textColorPrimary: WHITE,
    textColorQuaternary: WHITE_SECONDARY,

    textColorHoverQuaternary: ACCENT,
    colorHoverQuaternary: `${ACCENT}40`,

    textColorPressedQuaternary: ACCENT,
    colorPressedQuaternary: `${ACCENT}40`,
  },
  Tabs: {
    tabTextColorActiveLine: ACCENT,
    tabTextColorHoverLine: ACCENT_LIGHT,
    barColor: ACCENT,
  },
  Menu: {
    groupTextColor: GRAY,
    itemHeight: '28px',
    itemColorHover: 'transparent',
    itemColorActive: 'transparent',
    itemColorActiveHover: 'transparent',

    itemTextColorActive: ACCENT,
    itemIconColorActive: ACCENT,
    itemTextColorActiveHover: ACCENT,
    itemIconColorActiveHover: ACCENT,

    itemTextColorHover: ACCENT_LIGHT,
    itemIconColorHover: ACCENT_LIGHT,

    itemIndicatorColor: 'transparent',
    itemIndicatorColorHover: 'transparent',
    itemIndicatorColorActive: 'transparent',
  },
  Dropdown: {
    color: BG,
    optionColorHover: LIGHT_DARK,
    dividerColor: LIGHT,
    optionTextColor: WHITE,
    optionTextColorHover: ACCENT,
    optionIconColorHover: ACCENT,
  },
  Layout: {
    siderColor: LIGHT_DARK,
    color: DARK,
  },
  Popover: {
    color: MEDIUM,
    textColor: WHITE_SECONDARY,
    border: `1px solid ${LIGHT}`,
    borderRadius: '8px',
  },
  Upload: {
    itemColorHover: MEDIUM,
    itemColorActive: LIGHT,
  },
  Message: {
    color: MEDIUM,
    textColor: WHITE_SECONDARY,

    colorSuccess: MEDIUM,
    textColorSuccess: ACCENT,

    colorError: MEDIUM,
    textColorError: RED,

    colorInfo: MEDIUM,
    textColorInfo: WHITE_SECONDARY,

    colorWarning: MEDIUM,
    textColorWarning: YELLOW,

    borderRadius: '8px',
    boxShadow: `0 4px 6px -1px ${BLACK}40`,
  },
};
