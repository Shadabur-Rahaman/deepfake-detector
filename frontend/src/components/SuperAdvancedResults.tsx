// Super Advanced Results Display Component
import React from 'react';
import { Card, CardContent, Typography, Grid, Chip, Box } from '@mui/material';

export const SuperAdvancedResults = ({ results }) => {
  if (!results) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Super Advanced Detection Results
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2">Prediction</Typography>
            <Chip 
              label={results.prediction}
              color={results.prediction.includes('Authentic') ? 'success' : 'error'}
              size="large"
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2">Confidence</Typography>
            <Typography variant="h4">
              {(results.confidence * 100).toFixed(1)}%
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2">Processing Time</Typography>
            <Typography variant="h4">
              {results.processing_time.toFixed(1)}s
            </Typography>
          </Grid>
        </Grid>
        
        {results.super_advanced_details && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Features Used ({results.super_advanced_details.features_used?.length || 0}/12)
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {results.super_advanced_details.features_used?.map((feature, index) => (
                <Chip key={index} label={feature} color="primary" size="small" />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};