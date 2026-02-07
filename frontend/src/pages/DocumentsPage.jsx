import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Grid,
  Chip,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Search,
  MoreVert,
  Edit,
  Delete,
  Label,
  Visibility,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

const DocumentsPage = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getList();
      setDocuments(response.data.data.items);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个文档吗？')) {
      try {
        await documentsAPI.delete(id);
        fetchDocuments();
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };

  const handleMenuOpen = (event, doc) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedDoc(doc);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedDoc(null);
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (doc.summary && doc.summary.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">文档</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => navigate('/documents/new')}>
          新建文档
        </Button>
      </Box>

      <TextField
        fullWidth
        placeholder="搜索文档..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
        }}
        sx={{ mb: 4 }}
      />

      {loading ? (
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography>加载中...</Typography>
        </Box>
      ) : filteredDocuments.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchQuery ? '没有找到匹配的文档' : '还没有文档'}
          </Typography>
          <Typography variant="body2" color="text.disabled" sx={{ mb: 3 }}>
            {searchQuery ? '尝试其他关键词' : '从对话中整理或手动创建文档'}
          </Typography>
          {!searchQuery && (
            <Button variant="outlined" startIcon={<Add />} onClick={() => navigate('/documents/new')}>
              创建第一个文档
            </Button>
          )}
        </Box>
      ) : (
        <Grid container spacing={2}>
          {filteredDocuments.map((doc) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={doc.document_id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  border: '1px solid transparent',
                  '&:hover': {
                    boxShadow: 3,
                    borderColor: 'primary.main',
                    transform: 'translateY(-2px)',
                  },
                }}
                onClick={() => navigate(`/documents/${doc.document_id}`)}
              >
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        pr: 6,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {doc.title}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, doc)}
                      sx={{ position: 'absolute', top: 12, right: 12 }}
                    >
                      <MoreVert fontSize="small" />
                    </IconButton>
                  </Box>

                  {doc.summary && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        lineHeight: 1.6,
                      }}
                    >
                      {doc.summary}
                    </Typography>
                  )}

                  {doc.tags && doc.tags.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 'auto' }}>
                      {doc.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                          icon={<Label sx={{ fontSize: 14 }} />}
                          sx={{ borderRadius: 0, height: 24 }}
                        />
                      ))}
                    </Box>
                  )}

                  <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 2 }}>
                    更新于 {new Date(doc.updated_at).toLocaleDateString('zh-CN')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
        <MenuItem
          onClick={() => {
            navigate(`/documents/${selectedDoc?.document_id}`);
            handleCloseMenu();
          }}
        >
          <Visibility sx={{ mr: 1 }} /> 查看
        </MenuItem>
        <MenuItem
          onClick={() => {
            navigate(`/documents/${selectedDoc?.document_id}/edit`);
            handleCloseMenu();
          }}
        >
          <Edit sx={{ mr: 1 }} /> 编辑
        </MenuItem>
        <MenuItem
          onClick={(e) => {
            handleDeleteDocument(selectedDoc?.document_id, e);
            handleCloseMenu();
          }}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} /> 删除
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default DocumentsPage;
