"use client";

import React from "react";

const LANGUAGE_COLORS: Record<string, string> = {
  Python: "#3572A5",
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Go: "#00ADD8",
  Rust: "#dea584",
  Java: "#b07219",
  "C++": "#f34b7d",
  C: "#555555",
  "C#": "#178600",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Ruby: "#701516",
  PHP: "#4F5D95",
  Shell: "#89e051",
  Dockerfile: "#384d54",
};

interface LanguageBarProps {
  languages: Record<string, number>;
}

export function LanguageBar({ languages }: LanguageBarProps) {
  const totalBytes = Object.values(languages).reduce((a, b) => a + b, 0);

  if (!languages || totalBytes === 0) {
    return <div className="text-sm text-gray-500 italic">No language statistics detected</div>;
  }

  const langList = Object.entries(languages)
    .map(([lang, bytes]) => ({
      name: lang,
      percentage: Number(((bytes / totalBytes) * 100).toFixed(1)),
      color: LANGUAGE_COLORS[lang] || "#8b5cf6",
    }))
    .sort((a, b) => b.percentage - a.percentage);

  return (
    <div className="space-y-3">
      {/* Visual progress bar */}
      <div className="h-2.5 w-full bg-gray-800 rounded-full overflow-hidden flex">
        {langList.map((item) => (
          <div
            key={item.name}
            style={{ width: `${item.percentage}%`, backgroundColor: item.color }}
            className="h-full transition-all duration-500"
            title={`${item.name}: ${item.percentage}%`}
          />
        ))}
      </div>

      {/* Language legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs">
        {langList.slice(0, 6).map((item) => (
          <div key={item.name} className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block"
              style={{ backgroundColor: item.color }}
            />
            <span className="font-medium text-gray-300">{item.name}</span>
            <span className="text-gray-500">{item.percentage}%</span>
          </div>
        ))}
        {langList.length > 6 && (
          <span className="text-gray-500 font-medium">
            +{langList.length - 6} other languages
          </span>
        )}
      </div>
    </div>
  );
}
