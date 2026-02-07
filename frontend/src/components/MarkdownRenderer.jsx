import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Box, useTheme, Accordion, AccordionSummary, AccordionDetails, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const StyledMarkdown = styled(Box)(({ theme }) => ({
  '& h1': {
    fontSize: '2rem',
    fontWeight: 700,
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
    borderBottom: `1px solid ${theme.palette.divider}`,
    paddingBottom: theme.spacing(1),
  },
  '& h2': {
    fontSize: '1.5rem',
    fontWeight: 600,
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
    borderBottom: `1px solid ${theme.palette.divider}`,
    paddingBottom: theme.spacing(0.5),
  },
  '& h3': {
    fontSize: '1.25rem',
    fontWeight: 600,
    marginTop: theme.spacing(1.5),
    marginBottom: theme.spacing(0.75),
  },
  '& h4': {
    fontSize: '1rem',
    fontWeight: 600,
    marginTop: theme.spacing(1.5),
    marginBottom: theme.spacing(0.5),
  },
  '& h5, & h6': {
    fontSize: '0.875rem',
    fontWeight: 600,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(0.5),
  },
  '& p': {
    marginTop: 0,
    marginBottom: theme.spacing(1),
    lineHeight: 1.7,
  },
  '& a': {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    '&:hover': {
      textDecoration: 'underline',
    },
  },
  '& ul, & ol': {
    marginTop: 0,
    marginBottom: theme.spacing(1),
    paddingLeft: theme.spacing(2),
  },
  '& li': {
    marginBottom: theme.spacing(0.5),
    lineHeight: 1.7,
  },
  '& ul': {
    listStyleType: 'disc',
  },
  '& ol': {
    listStyleType: 'decimal',
  },
  '& blockquote': {
    borderLeft: `4px solid ${theme.palette.primary.main}`,
    paddingLeft: theme.spacing(2),
    marginLeft: 0,
    marginRight: 0,
    marginBottom: theme.spacing(1),
    fontStyle: 'italic',
    color: theme.palette.text.secondary,
    backgroundColor: theme.palette.background.default,
    padding: theme.spacing(1),
  },
  '& code': {
    fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
    fontSize: '0.875em',
    backgroundColor: theme.palette.background.default,
    padding: '0.2em 0.4em',
    borderRadius: '3px',
    border: `1px solid ${theme.palette.divider}`,
  },
  '& pre': {
    backgroundColor: theme.palette.mode === 'dark' ? '#1e1e1e' : '#f5f5f5',
    padding: theme.spacing(2),
    borderRadius: 1,
    overflow: 'auto',
    marginBottom: theme.spacing(1),
    border: `1px solid ${theme.palette.divider}`,
  },
  '& pre code': {
    backgroundColor: 'transparent',
    padding: 0,
    border: 'none',
    fontSize: '0.875rem',
    lineHeight: 1.5,
  },
  '& table': {
    width: '100%',
    borderCollapse: 'collapse',
    marginBottom: theme.spacing(2),
    border: `1px solid ${theme.palette.divider}`,
  },
  '& th, & td': {
    padding: theme.spacing(1),
    border: `1px solid ${theme.palette.divider}`,
    textAlign: 'left',
  },
  '& th': {
    backgroundColor: theme.palette.background.default,
    fontWeight: 600,
  },
  '& img': {
    maxWidth: '100%',
    height: 'auto',
    borderRadius: 1,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  '& hr': {
    border: 'none',
    borderTop: `1px solid ${theme.palette.divider}`,
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
}));

// 提取  标签内容的函数
const extractThinkContent = (content) => {
  const thinkRegex = /([\s\S]*?)<\/think>/g;
  const matches = [];
  let match;
  let cleanContent = content;

  while ((match = thinkRegex.exec(content)) !== null) {
    matches.push(match[1].trim());
  }

  // 移除所有 think 标签
  cleanContent = content.replace(thinkRegex, '');

  return { thinkContents: matches, cleanContent };
};

const ThinkingAccordion = styled(Accordion)(({ theme }) => ({
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: '8px !important',
  boxShadow: 'none',
  '&::before': {
    display: 'none',
  },
  '&.MuiAccordion-root.Mui-expanded': {
    margin: theme.spacing(1, 0),
  },
}));

const ThinkingSummary = styled(AccordionSummary)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  borderBottom: `1px solid ${theme.palette.divider}`,
  minHeight: '48px !important',
  '& .MuiAccordionSummary-content': {
    margin: theme.spacing(0.75, 2),
  },
  '& .MuiAccordionSummary-content.Mui-expanded': {
    margin: theme.spacing(0.75, 2),
  },
}));

const ThinkingDetails = styled(AccordionDetails)(({ theme }) => ({
  padding: theme.spacing(1.5, 2),
  backgroundColor: theme.palette.background.paper,
  borderTop: `1px solid ${theme.palette.divider}`,
  '& .markdown-content': {
    marginTop: 0,
    marginBottom: 0,
  },
}));

const MarkdownRenderer = ({ content, isDarkMode = false }) => {
  const theme = useTheme();
  const darkMode = isDarkMode ?? theme.palette.mode === 'dark';
  const [thinkingExpanded, setThinkingExpanded] = useState(false);

  // 提取 think 内容
  const { thinkContents, cleanContent } = extractThinkContent(content);

  return (
    <StyledMarkdown>
      {/* 思考中～折叠面板 */}
      {thinkContents.length > 0 && (
        <ThinkingAccordion
          expanded={thinkingExpanded}
          onChange={() => setThinkingExpanded(!thinkingExpanded)}
        >
          <ThinkingSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle2" color="text.secondary">
              ☁️ 思考中～
            </Typography>
          </ThinkingSummary>
          <ThinkingDetails>
            {thinkContents.map((thinkContent, index) => (
              <Box key={index} className="markdown-content" sx={{ mb: index < thinkContents.length - 1 ? 2 : 0 }}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeRaw]}
                  components={{
                    code({ inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      const language = match ? match[1] : '';
                      return !inline && language ? (
                        <SyntaxHighlighter
                          style={darkMode ? vscDarkPlus : vs}
                          language={language}
                          PreTag="div"
                          customStyle={{
                            margin: '8px 0',
                            borderRadius: '4px',
                            fontSize: '14px',
                          }}
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {thinkContent}
                </ReactMarkdown>
              </Box>
            ))}
          </ThinkingDetails>
        </ThinkingAccordion>
      )}

      {/* 主要内容 */}
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          code({ inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            return !inline && language ? (
              <SyntaxHighlighter
                style={darkMode ? vscDarkPlus : vs}
                language={language}
                PreTag="div"
                customStyle={{
                  margin: '8px 0',
                  borderRadius: '4px',
                  fontSize: '14px',
                }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          a({ children, href, ...props }) {
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
                {children}
              </a>
            );
          },
        }}
      >
        {cleanContent}
      </ReactMarkdown>
    </StyledMarkdown>
  );
};

export default MarkdownRenderer;
