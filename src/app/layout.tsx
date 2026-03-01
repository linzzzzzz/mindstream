export const metadata = {
  title: "MindStream - AI Thought Leader Content Aggregator",
  description: "Discover and track AI content from thought leaders",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
