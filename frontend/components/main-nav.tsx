'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

import ThemeToggle from '@/components/theme-toggle';
import UserMenu from '@/components/user-menu';

import { cn } from '@/lib/utils';

export function MainNav({
	className,
	...props
}: React.HTMLAttributes<HTMLElement>) {
	return (
		<div className="border-b w-full">
			<div className="flex h-16 items-center justify-between">
				<nav
					className={cn('flex items-center space-x-4 lg:space-x-6', className)}
					{...props}
				>
					<NavOption href="/dashboard">Dashboard</NavOption>
					<NavOption href="/simulation">Simulation</NavOption>
					<NavOption href="/settings">Settings</NavOption>
				</nav>
				<div className=" flex items-center space-x-4">
					<ThemeToggle />
					<UserMenu />
				</div>
			</div>
		</div>
	);
}

const NavOption = ({
	children,
	href
}: {
	children: ReactNode;
	href: string;
}) => {
	const path = usePathname();

	return (
		<Link
			href={href}
			className={cn(
				'text-sm font-medium  transition-colors hover:text-primary',
				path.includes(href) ? '' : 'text-muted-foreground'
			)}
		>
			{children}
		</Link>
	);
};
