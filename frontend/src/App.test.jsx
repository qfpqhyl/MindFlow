import React from 'react';

function App() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#FFFFFF',
      color: '#000000',
      fontFamily: 'Inter, sans-serif'
    }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '1rem' }}>
        MindFlow
      </h1>
      <p style={{ fontSize: '1.25rem', color: '#666666' }}>
        思流如潮
      </p>
      <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #E0E0E0' }}>
        <p>前端正在运行...</p>
      </div>
    </div>
  );
}

export default App;
