import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "k";
  }
  return num.toString();
}

export function parseGitHubUrl(input: string): { owner: string; repo: string } | null {
  const clean = input.trim().replace(/\.git$/, "");
  const regex = /^(?:https?:\/\/github\.com\/)?([a-zA-Z0-9_.-]+)\/([a-zA-Z0-9_.-]+)\/?$/;
  const match = clean.match(regex);
  if (!match) return null;
  return { owner: match[1], repo: match[2] };
}
