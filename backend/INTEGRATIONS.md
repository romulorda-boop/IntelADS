# Fontes externas — sincronização de apps

## Google Play

- Pacote Python fixado: [`google-play-scraper` 1.2.7 no PyPI](https://pypi.org/project/google-play-scraper/).
- Referência de uso/campos: [README do projeto](https://github.com/JoMingyu/google-play-scraper/blob/master/README.md).
- A chamada `app(package_id, lang="pt_BR", country="br")` retorna campos como `installs`, `minInstalls`, `score`, `icon`, `genre` e `genreId`. `installs` é a faixa pública de instalações da listagem, não uma contagem exata de downloads.
- Teste real realizado em 2026-10-06 com `com.supercell.brawlstars`: título `Brawl Stars`, faixa `500.000.000+`, rating aproximadamente `4.47`, gênero `Ação`, ícone HTTPS do Google Play. O resultado é dinâmico e pode mudar.
- O pacote faz scraping de endpoints da loja, não é uma API oficial do Google; disponibilidade, formato e acesso podem mudar ou sofrer bloqueio/rate limit.

## App Store / iTunes Lookup

- [Documentação Apple — iTunes Search API](https://performance-partners.apple.com/search-api) e [exemplos de lookup por ID](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/LookupExamples.html).
- Lookup usado: `https://itunes.apple.com/lookup?id=<trackId>&country=br`.
- Metadados úteis retornados incluem `trackName`, `averageUserRating`, `artworkUrl512` e `primaryGenreName`. A consulta pública não contém um campo de downloads/instalações; após sincronização iOS, o valor de downloads fica nulo e a interface informa “Não divulgado pela loja”.
- Teste real realizado em 2026-10-06 com o track ID `1229016807`: `Brawl Stars`, desenvolvedor Supercell, gênero Games, rating público e ícone HTTPS. Downloads não foram retornados.
- A documentação do Apple Services Performance Partner Program informa que o Search API é limitado a aproximadamente 20 chamadas por minuto, sujeito a mudança; evitar loops de atualização.

Ambas as integrações são somente leitura nas lojas. Não são necessárias chaves nem novos conectores para os endpoints públicos usados pelo MVP.
