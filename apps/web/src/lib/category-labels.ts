const adCategoryNames: Record<string, string> = {
  games: "Jogos",
  ecommerce: "E-commerce",
  apps: "Apps / Utilitários",
  finance: "Finanças",
  infoproducts: "Infoprodutos",
};

const storeCategoryNames: Record<string, string> = {
  acao: "Ação",
  action: "Ação",
  games: "Jogos",
  game: "Jogos",
  estrategia: "Estratégia",
  strategy: "Estratégia",
  puzzle: "Quebra-cabeças",
  puzzles: "Quebra-cabeças",
  racing: "Corrida",
  corrida: "Corrida",
  arcade: "Arcade",
  casual: "Casual",
  "role playing": "RPG",
  "role-playing": "RPG",
  "health & fitness": "Saúde e fitness",
  "health and fitness": "Saúde e fitness",
  education: "Educação",
  productivity: "Produtividade",
  lifestyle: "Estilo de vida",
  finance: "Finanças",
};

export function labelAdCategory(category: string): string {
  return adCategoryNames[category] ?? category;
}

export function labelStoreCategory(category: string | null | undefined): string | null {
  if (!category?.trim()) return null;
  const value = category.trim();
  const normalized = value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/^game[_\s-]+/, "")
    .replace(/[_-]+/g, " ")
    .trim();
  return storeCategoryNames[normalized] ?? value;
}
