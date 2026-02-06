import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#000000',
      light: '#333333',
      dark: '#000000',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FFFFFF',
      light: '#FFFFFF',
      dark: '#CCCCCC',
      contrastText: '#000000',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FAFAFA',
    },
    text: {
      primary: '#000000',
      secondary: '#666666',
      disabled: '#999999',
    },
    divider: '#E0E0E0',
    error: {
      main: '#000000',
    },
    success: {
      main: '#000000',
    },
    warning: {
      main: '#000000',
    },
    info: {
      main: '#000000',
    },
  },
  typography: {
    fontFamily: '"Inter", "Helvetica Neue", Helvetica, Arial, sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 0,
  },
  shadows: [
    'none',
    '0 1px 3px rgba(0,0,0,0.08)',
    '0 1px 6px rgba(0,0,0,0.12)',
    '0 3px 12px rgba(0,0,0,0.15)',
    '0 6px 24px rgba(0,0,0,0.18)',
    '0 12px 48px rgba(0,0,0,0.20)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          border: '1px solid #000',
          borderRadius: 0,
          padding: '12px 24px',
          '&:hover': {
            backgroundColor: '#000',
            color: '#FFF',
            boxShadow: 'none',
          },
        },
        contained: {
          backgroundColor: '#000',
          color: '#FFF',
          '&:hover': {
            backgroundColor: '#333',
            boxShadow: 'none',
          },
        },
        outlined: {
          borderColor: '#000',
          color: '#000',
          '&:hover': {
            backgroundColor: '#000',
            color: '#FFF',
            border: '1px solid #000',
          },
        },
        text: {
          color: '#000',
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.04)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 0,
            '& fieldset': {
              borderColor: '#E0E0E0',
              borderWidth: '1px',
            },
            '&:hover fieldset': {
              borderColor: '#000',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#000',
              borderWidth: '1px',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          border: '1px solid #E0E0E0',
          boxShadow: 'none',
          transition: 'box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: '#E0E0E0',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.04)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFF',
          color: '#000',
          borderBottom: '1px solid #E0E0E0',
          boxShadow: 'none',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #E0E0E0',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            backgroundColor: 'rgba(0,0,0,0.04)',
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.08)',
            },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          '&.Mui-selected': {
            color: '#000',
          },
        },
      },
    },
  },
});

export default theme;
