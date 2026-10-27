import React, { useState, useEffect } from "react";
import {
  FolderKanban,
  FileText,
  FileCode,
  FileSpreadsheet,
  FileJson,
  Folder,
  Search,
  Sparkles,
  ChevronRight,
  Home,
  ArrowUpDown,
  UploadCloud,
  HardDrive,
  FileCheck,
  ShieldAlert,
} from "lucide-react";
import { api } from "../../api";
import type { FileItem } from "../../types";

interface FilesScreenProps {
  files: FileItem[]; // fallback/initial
  onUploadFile: (file: File) => void;
  onAnalyzeFile: (file: FileItem) => void;
}

export const FilesScreen: React.FC<FilesScreenProps> = ({
  onUploadFile,
  onAnalyzeFile,
}) => {
  const [currentPath, setCurrentPath] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileList, setFileList] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [sortBy, setSortBy] = useState("type"); // name, size, type
  const [sortDesc, setSortDesc] = useState(false);

  const loadFiles = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listFiles(path || undefined);
      if (res && res.files) {
        setFileList(res.files);
      } else {
        setError("Empty workspace file layout received.");
      }
    } catch (e: any) {
      console.error("Failed to load workspace files:", e);
      setError("Unable to communicate with the local Saarthi filesystem service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  // Navigate back to a specific segment of the path
  const navigateToBreadcrumb = (index: number) => {
    if (index === -1) {
      setCurrentPath("");
      return;
    }
    const separator = currentPath.includes("\\") ? "\\" : "/";
    const parts = currentPath.split(separator);
    const targetPath = parts.slice(0, index + 1).join(separator);
    setCurrentPath(targetPath);
  };

  const getBreadcrumbs = () => {
    if (!currentPath) return [];
    const separator = currentPath.includes("\\") ? "\\" : "/";
    return currentPath.split(separator).filter(Boolean);
  };

  const handleRowClick = (item: any) => {
    if (item.is_directory) {
      setCurrentPath(item.path);
    }
  };

  const getFileIcon = (name: string, isDir: boolean) => {
    if (isDir) return <Folder className="text-amber-400" size={18} />;
    const ext = name.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "py":
      case "ts":
      case "tsx":
      case "js":
      case "jsx":
      case "html":
      case "css":
        return <FileCode className="text-purple-400" size={18} />;
      case "pdf":
        return <FileText className="text-rose-400" size={18} />;
      case "json":
        return <FileJson className="text-sky-400" size={18} />;
      case "md":
        return <FileText className="text-emerald-400" size={18} />;
      default:
        return <FileSpreadsheet className="text-zinc-400" size={18} />;
    }
  };

  // Filter & Sort
  const filtered = fileList.filter((f) => {
    const matchesSearch = f.name.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;

    if (filterType === "all") return true;
    if (filterType === "folder") return f.is_directory;
    
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (filterType === "code") {
      return ["py", "ts", "tsx", "js", "jsx", "html", "css", "md"].includes(ext || "");
    }
    if (filterType === "pdf") return ext === "pdf";
    if (filterType === "json") return ext === "json";
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    let comp = 0;
    if (sortBy === "name") {
      comp = a.name.localeCompare(b.name);
    } else if (sortBy === "size") {
      comp = (a.size || 0) - (b.size || 0);
    } else if (sortBy === "type") {
      comp = (a.is_directory ? 0 : 1) - (b.is_directory ? 0 : 1);
      if (comp === 0) {
        comp = a.name.localeCompare(b.name);
      }
    }
    return sortDesc ? -comp : comp;
  });

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(field);
      setSortDesc(false);
    }
  };

  const formatSize = (bytes: number | null) => {
    if (bytes === null) return "-";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-hidden select-none space-y-4">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl shrink-0">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <FolderKanban size={20} className="text-[#F59E0B]" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              WORKSPACE EXPLORER
            </h2>
          </div>
          <p className="text-[11px] text-white/50 flex items-center gap-1.5 font-mono">
            <HardDrive size={12} className="text-[#F59E0B]" /> Sandboxed sandbox: E:\Saarthi
          </p>
        </div>
      </div>

      {/* Breadcrumbs Navigation */}
      <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#0D0D0D] border border-white/5 text-[11px] font-mono overflow-x-auto shrink-0">
        <button
          onClick={() => navigateToBreadcrumb(-1)}
          className="text-white/40 hover:text-[#F59E0B] flex items-center gap-1"
        >
          <Home size={12} />
          <span>saarthi-workspace</span>
        </button>

        {getBreadcrumbs().map((part, index) => (
          <React.Fragment key={index}>
            <ChevronRight size={10} className="text-white/20" />
            <button
              onClick={() => navigateToBreadcrumb(index)}
              className="text-white/40 hover:text-[#F59E0B] max-w-[120px] truncate"
            >
              {part}
            </button>
          </React.Fragment>
        ))}
      </div>

      {/* Search and Filters Strip */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 shrink-0">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search current folder..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#141414] border border-white/5 text-white placeholder-white/20 text-xs focus:outline-none focus:border-[#F59E0B]/80 font-sans"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {[
            { id: "all", label: "All Items" },
            { id: "folder", label: "Folders" },
            { id: "code", label: "Code / Markdown" },
            { id: "pdf", label: "PDF Documents" },
            { id: "json", label: "JSON Configurations" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setFilterType(item.id)}
              className={`px-3 py-1.5 rounded-xl text-[11px] font-medium transition-all cursor-pointer ${
                filterType === item.id
                  ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30"
                  : "bg-[#141414] text-white/40 border border-white/5 hover:text-white"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Explorer Content Table */}
      <div className="flex-1 overflow-y-auto border border-white/5 rounded-2xl bg-[#0D0D0D]">
        {error ? (
          <div className="h-full flex flex-col items-center justify-center p-8 text-center space-y-4 max-w-sm mx-auto">
            <div className="p-3.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400">
              <ShieldAlert size={28} className="animate-pulse" />
            </div>
            <div className="space-y-1.5">
              <h4 className="text-white font-mono text-xs font-bold uppercase tracking-wider">
                WORKSPACE OFFLINE
              </h4>
              <p className="text-white/40 text-xs leading-relaxed">
                {error}
              </p>
            </div>
            <button
              onClick={() => loadFiles(currentPath)}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white font-mono text-[11px] rounded-xl border border-white/5 cursor-pointer transition-colors"
            >
              Retry Connection
            </button>
          </div>
        ) : loading ? (
          <div className="h-full flex items-center justify-center text-xs font-mono text-white/40 gap-2">
            <span className="w-2 h-2 rounded-full bg-[#F59E0B] animate-ping" />
            <span>Scanning directory trees...</span>
          </div>
        ) : sorted.length > 0 ? (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-white/5 text-white/30 font-mono font-medium text-[10px] uppercase select-none">
                <th
                  onClick={() => handleSort("name")}
                  className="p-3 pl-4 cursor-pointer hover:text-white transition-colors"
                >
                  <span className="flex items-center gap-1.5">
                    Name <ArrowUpDown size={10} />
                  </span>
                </th>
                <th
                  onClick={() => handleSort("type")}
                  className="p-3 cursor-pointer hover:text-white transition-colors w-32"
                >
                  <span className="flex items-center gap-1.5">
                    Type <ArrowUpDown size={10} />
                  </span>
                </th>
                <th
                  onClick={() => handleSort("size")}
                  className="p-3 cursor-pointer hover:text-white transition-colors w-32"
                >
                  <span className="flex items-center gap-1.5">
                    Size <ArrowUpDown size={10} />
                  </span>
                </th>
                <th className="p-3 text-right pr-4 w-44">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {sorted.map((item, idx) => (
                <tr
                  key={idx}
                  onClick={() => handleRowClick(item)}
                  className={`hover:bg-white/5 transition-colors cursor-pointer ${
                    item.is_directory ? "font-semibold" : ""
                  }`}
                >
                  <td className="p-3 pl-4 flex items-center gap-2.5 truncate max-w-sm">
                    {getFileIcon(item.name, item.is_directory)}
                    <span className="text-white/80 group-hover:text-white truncate">
                      {item.name}
                    </span>
                  </td>
                  <td className="p-3 font-mono text-[10px] text-white/40">
                    {item.is_directory ? "Directory" : item.name.split(".").pop()?.toUpperCase() || "File"}
                  </td>
                  <td className="p-3 font-mono text-[10px] text-white/40">
                    {formatSize(item.size)}
                  </td>
                  <td className="p-3 text-right pr-4">
                    {!item.is_directory && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const fItem: FileItem = {
                            id: `file-explore-${idx}`,
                            name: item.name,
                            path: item.path,
                            is_dir: false,
                            size: formatSize(item.size),
                            type: item.name.endsWith(".pdf") ? "pdf" : "code",
                            indexed: true,
                            lastModified: "",
                            tags: [],
                            status: "ready",
                          };
                          onAnalyzeFile(fItem);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-[#F59E0B]/10 hover:bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/20 text-[10px] font-semibold transition-all inline-flex items-center gap-1 cursor-pointer"
                      >
                        <Sparkles size={11} />
                        <span>Analyze</span>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center text-white/30 space-y-2 py-16 font-mono">
            <HardDrive size={30} className="text-white/10" />
            <p className="text-xs">No workspace items match filter rules.</p>
          </div>
        )}
      </div>
    </div>
  );
};

