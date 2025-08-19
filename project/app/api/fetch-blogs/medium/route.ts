import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const mediumSources = ['towardsdatascience', 'towardsai'];
        const allBlogs = [];

        for (const source of mediumSources) {
            const response = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/${source}`);
            if (response.ok) {
                const data = await response.json();
                const blogs = data.items?.slice(0, 5).map((item: any, index: number) => ({
                    id: `medium-${source}-${index}`,
                    title: item.title,
                    excerpt: item.description?.replace(/<[^>]*>/g, '').substring(0, 200) + '...',
                    url: item.link,
                    source: `Medium - ${source}`,
                    date: new Date(item.pubDate).toLocaleDateString()
                }));
                allBlogs.push(...blogs);
            }
        }

    } catch (error) {
        return NextResponse.json({
            success: false,
            error: (error as Error).message
        }, { status: 500 });
    }

}
