"use client";

import React, { useState, useRef } from "react";
import { Upload, FileText, AlertCircle, CheckCircle, Clock, Mail, Brain, Sparkles } from "lucide-react";

type ApiResponse = {
  category: "Produtivo" | "Improdutivo" | string;
  confidence: number;
  suggested_reply: string;
  language: string;
  preview: string;
  provider?: string;
};

const UploadForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [stemming, setStemming] = useState(false);
  const [provider, setProvider] = useState("openai");
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const apiBase = "http://localhost:8000";

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setFile(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const onSubmit = async () => {
    setError("");
    setResp(null);

    if (!file) {
      setError("Por favor, selecione um arquivo .pdf ou .txt.");
      return;
    }

    const ext = file.name.toLowerCase();
    if (!ext.endsWith(".pdf") && !ext.endsWith(".txt")) {
      setError("Formato inválido. Envie apenas arquivos .pdf ou .txt.");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("file", file);

      const url = `${apiBase}/classify?stemming=${stemming ? "true" : "false"}&provider=${provider}`;

      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Erro ${res.status} - Falha na comunicação com o servidor`);
      }

      const data: ApiResponse = await res.json();
      setResp(data);
    } catch (err: any) {
      setError(err?.message || "Falha ao processar o arquivo. Verifique sua conexão e tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-4xl p-6">
        {/* Header */}
        <header className="mb-10 text-center">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-black to-blue-600 rounded-2xl shadow-lg">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-black to-blue-700 bg-clip-text text-transparent">
              Classificador Inteligente de E-mails
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Analise automaticamente seus e-mails para determinar se são produtivos ou improdutivos.
            Nossa IA também sugere respostas automáticas personalizadas.
          </p>
        </header>

        {/* Upload Form */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 mb-8">
          <div className="space-y-6">
            {/* File Upload Area */}
            <div
              className={`relative border-2 border-dashed rounded-2xl p-8 transition-all duration-200 ${
                dragOver
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />

              <div className="text-center space-y-4">
                <div className="inline-flex p-4 bg-blue-100 rounded-full">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>

                {!file ? (
                  <>
                    <div>
                      <p className="text-lg font-medium text-gray-700 mb-2">
                        Arraste e solte ou clique para selecionar
                      </p>
                      <p className="text-sm text-gray-500">
                        Suporte para arquivos .PDF e .TXT (máx. 10MB)
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="bg-gray-50 rounded-xl p-4 border">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="w-6 h-6 text-blue-600" />
                        <div className="text-left">
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={removeFile}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition-colors"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-4 bg-gray-50 rounded-xl p-4">
              <label className="inline-flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={stemming}
                  onChange={(e) => setStemming(e.target.checked)}
                  className="w-5 h-5 text-black rounded focus:ring-black"
                />
                <div>
                  <span className="font-medium text-gray-900">Ativar Stemming PT-BR</span>
                  <p className="text-sm text-gray-600">Melhora a análise reduzindo palavras ao radical</p>
                </div>
              </label>

              {/* Select provider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Escolher modelo
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full border rounded-lg p-2"
                >
                  <option value="openai">OpenAI (GPT-4o-mini)</option>
                  <option value="huggingface">HuggingFace (mDeBERTa-v3-xnli)</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={onSubmit}
              disabled={loading || !file}
              className="w-full inline-flex items-center justify-center gap-3 cursor-pointer rounded-xl bg-black px-6 py-4 text-white font-bold text-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl"
            >
              {loading ? (
                <>
                  <Clock className="w-5 h-5 animate-spin" />
                  Processando arquivo...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Analisar E-mail
                </>
              )}
            </button>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {resp && (
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 space-y-6">
            {/* Classification Header */}
            <div className="flex items-center justify-between pb-6 border-b">
              <div className="flex items-center gap-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Análise Concluída</h2>
                  <p className="text-gray-600">Resultado da classificação automática</p>
                </div>
              </div>

              <div className="text-right">
                <div
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold ${
                    resp.category === "Produtivo"
                      ? "bg-green-100 text-green-800 border border-green-200"
                      : "bg-amber-100 text-amber-800 border border-amber-200"
                  }`}
                >
                  {resp.category}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Confiança: {(resp.confidence * 100).toFixed(1)}% | Modelo: {resp.provider || provider}
                </p>
              </div>
            </div>

            {/* Suggested Reply */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-black" />
                <h3 className="text-lg font-semibold text-gray-900">Resposta Sugerida</h3>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">{resp.suggested_reply}</p>
              </div>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => navigator.clipboard.writeText(resp.suggested_reply)}
                  className="px-4 py-2 bg-blue-100 text-black rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
                >
                  Copiar Resposta
                </button>
              </div>
            </div>

            {/* Preview */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Prévia do Conteúdo
                <span className="text-xs bg-gray-200 px-2 py-1 rounded-full">
                  {resp.language}
                </span>
              </h4>
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <p className="text-sm text-gray-700 leading-relaxed">{resp.preview}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default UploadForm;
