const links = document.getElementsByTagName("a");

var href_links = []

for (let link of links) {
	let href = link.getAttribute("href");
	
	if (href) {
		href_links.push(href);
	}
}

const unique_hrefs = [...new Set(href_links)];

console.log(unique_hrefs);
