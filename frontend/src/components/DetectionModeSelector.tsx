// Detection Mode Selector Component
import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, FormHelperText } from '@mui/material';

export const DetectionModeSelector = ({ value, onChange }) => {
  const modes = [
    { value: 'traditional', label: 'Traditional Detection' },
    { value: 'modern-ai', label: 'Modern AI Detection' },
    { value: 'hybrid', label: 'Hybrid Detection' },
    { value: 'super-advanced', label: 'Super Advanced Detection (All 12 Features)' }
  ];

  return (
    <FormControl fullWidth>
      <InputLabel>Detection Mode</InputLabel>
      <Select
        value={value}
        label="Detection Mode"
        onChange={onChange}
      >
        {modes.map((mode) => (
          <MenuItem key={mode.value} value={mode.value}>
            {mode.label}
          </MenuItem>
        ))}
      </Select>
      <FormHelperText>
        Choose the detection mode. Super Advanced uses all 12 advanced features.
      </FormHelperText>
    </FormControl>
  );
};