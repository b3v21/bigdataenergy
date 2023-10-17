'use client';

import { useEffect } from 'react';

export default function Layout({ children }: { children: React.ReactNode }) {
	useEffect(() => {
		document.documentElement.classList.remove('dark');
	}, []);
	return <div>{children}</div>;
}
