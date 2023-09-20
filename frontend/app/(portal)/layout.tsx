'use client';

import { MainNav } from '@/components/main-nav';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export default function RootLayout({
	children
}: {
	children: React.ReactNode;
}) {
	const queryClient = new QueryClient();

	return (
		<div className="flex-col flex h-screen">
			<div className="border-b">
				<div className="flex h-16 items-center px-4">
					<MainNav className="mx-6" />
				</div>
			</div>
			<div className="flex-1 space-y-4 p-8 pt-6">
				<QueryClientProvider client={queryClient}>
					{children}
				</QueryClientProvider>
			</div>
		</div>
	);
}
