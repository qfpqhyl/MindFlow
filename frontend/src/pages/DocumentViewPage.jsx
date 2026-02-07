import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Chip,
  Divider,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  ArrowBack,
  Edit,
} from '@mui/icons-material';
import { Label } from '@mui/icons-material';
import { documentsAPI } from '../services/api';
import MarkdownRenderer from '../components/MarkdownRenderer';

const DocumentViewPage = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);

  useEffect(() => {
    fetchDocument();
  }, [documentId]);

  const fetchDocument = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getDetail(documentId);
      setDocument(response.data.data);
    } catch (error) {
      console.error('Failed to fetch document:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          height: 'calc(100vh - 120px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!document) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            文档不存在
          </Typography>
          <Button variant="contained" onClick={() => navigate('/documents')} sx={{ mt: 2 }}>
            返回文档列表
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* 头部 */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <IconButton onClick={() => navigate('/documents')}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" sx={{ flex: 1, fontWeight: 600 }}>
          {document.title}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Edit />}
          onClick={() => navigate(`/documents/${documentId}/edit`)}
        >
          编辑
        </Button>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* 元信息 */}
      <Box sx={{ mb: 4 }}>
        {document.summary && (
          <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              摘要
            </Typography>
            <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
              {document.summary}
            </Typography>
          </Paper>
        )}

        {document.tags && document.tags.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {document.tags.map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                variant="outlined"
                icon={<Label sx={{ fontSize: 16 }} />}
                sx={{ borderRadius: 0 }}
              />
            ))}
          </Box>
        )}

        <Typography variant="caption" color="text.disabled">
          创建于 {new Date(document.created_at).toLocaleString('zh-CN')}
          {' • '}
          更新于 {new Date(document.updated_at).toLocaleString('zh-CN')}
        </Typography>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* 内容 */}
      <Paper sx={{ p: 4 }}>
        <MarkdownRenderer content={document.content || '暂无内容'} />
      </Paper>
    </Container>
  );
};

export default DocumentViewPage;
