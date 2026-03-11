Jekyll::Hooks.register [:posts, :pages], :post_render do |doc|
  next unless doc.output_ext == '.html'

  doc.output = doc.output.gsub(/<a\s[^>]*href="https?:\/\/[^"]*"[^>]*>/i) do |tag|
    next tag if tag.include?('target=')

    tag.sub(/>$/, ' target="_blank" rel="noopener noreferrer">')
  end
end
