'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api';
import { FILE_VALIDATION } from '@/lib/constants';
import { isValidFileType, isValidFileSize, cn } from '@/lib/utils';
import { FilePreview } from './FilePreview';
import { UploadProgress } from './UploadProgress';
import type { UploadProgress as UploadProgressType } from '@/types';

interface UploadCardProps {
  userId: string;
}

/**
 * Document upload card with drag & drop
 */
export function UploadCard({ userId }: UploadCardProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploads, setUploads] = useState<UploadProgressType[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Validate files
    const validFiles: File[] = [];

    acceptedFiles.forEach((file) => {
      if (!isValidFileType(file , FILE_VALIDATION.ACCEPTED_TYPES)) {
        toast.error(`${file.name}: Invalid file type. Only PDF, TXT, and DOCX are allowed.`);
        return;
      }

      if (!isValidFileSize(file, FILE_VALIDATION.MAX_SIZE)) {
        toast.error(
          `${file.name}: File too large. Maximum size is ${FILE_VALIDATION.MAX_SIZE_MB}MB.`
        );
        return;
      }

      validFiles.push(file);
    });

    setSelectedFiles((prev) => [...prev, ...validFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: FILE_VALIDATION.ACCEPTED_TYPES,
    maxSize: FILE_VALIDATION.MAX_SIZE,
  });

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    // Initialize upload progress for each file
    const initialUploads: UploadProgressType[] = selectedFiles.map((file) => ({
      file,
      status: 'uploading',
      progress: 0,
    }));

    setUploads(initialUploads);

    // Upload files sequentially
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];

      try {
        const response = await apiClient.uploadDocument(
          file,
          userId,
          undefined,
          (progress) => {
            setUploads((prev) =>
              prev.map((upload, idx) =>
                idx === i ? { ...upload, progress } : upload
              )
            );
          }
        );

        // Mark as success
        setUploads((prev) =>
          prev.map((upload, idx) =>
            idx === i
              ? {
                  ...upload,
                  status: 'success',
                  progress: 100,
                  document: response.document,
                }
              : upload
          )
        );

        toast.success(`${file.name} uploaded successfully`);
      } catch (error: any) {
        // Mark as error
        setUploads((prev) =>
          prev.map((upload, idx) =>
            idx === i
              ? {
                  ...upload,
                  status: 'error',
                  error: error.message || 'Upload failed',
                }
              : upload
          )
        );

        toast.error(`Failed to upload ${file.name}`);
      }
    }

    // Clear selected files after upload
    setSelectedFiles([]);
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Documents</CardTitle>
        <CardDescription>
          Upload PDF, TXT, or DOCX files to enhance the AI's knowledge base
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all',
            isDragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800/50'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-12 h-12 text-gray-400"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
              />
            </svg>
            <p className="text-sm text-gray-300">
              {isDragActive
                ? 'Drop files here...'
                : 'Drag & drop files here, or click to select'}
            </p>
            <p className="text-xs text-gray-500">
              PDF, TXT, DOCX • Max {FILE_VALIDATION.MAX_SIZE_MB}MB
            </p>
          </div>
        </div>

        {/* Selected files */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-white">Selected Files</h3>
            {selectedFiles.map((file, index) => (
              <FilePreview key={index} file={file} onRemove={() => handleRemoveFile(index)} />
            ))}
            <button
              onClick={handleUpload}
              className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
            >
              Upload {selectedFiles.length} {selectedFiles.length === 1 ? 'file' : 'files'}
            </button>
          </div>
        )}

        {/* Upload progress */}
        {uploads.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-white">Upload Progress</h3>
            {uploads.map((upload, index) => (
              <UploadProgress key={index} upload={upload} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
