import LoginForm from '@/app/(login)/components/login-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Metadata } from 'next';

export const metadata: Metadata = {
	title: 'Login | Big Data Energy'
};

export default function Login() {
	return (
		<div className="container relative grid h-screen min-w-full items-center justify-center">
			<video
				className="absolute inset-0 filter grayscale blur-sm object-cover w-full h-full"
				autoPlay
				loop
				muted
				src="https://www.shutterstock.com/shutterstock/videos/7782712/preview/stock-footage-commute-out-of-brisbane-city-time-lapse-brisbane-queensland-australia-october.webm "
			/>

			<Card className="w-[350px] z-10 font-light bg-white border-gray-300">
				<CardHeader>
					{/* eslint-disable-next-line @next/next/no-img-element */}
					<img src="/logo.png" alt="logo" className="w-50 h-20 mx-auto" />
					<CardTitle className="text-center text-slate-950">Sign In</CardTitle>
				</CardHeader>
				<CardContent>
					<LoginForm />
				</CardContent>
			</Card>

			<div className="absolute left-10 top-10 m-0 flex items-center text-lg font-medium lg:hidden">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					strokeWidth="2"
					strokeLinecap="round"
					strokeLinejoin="round"
					className="mr-2 h-6 w-6"
				>
					<path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
				</svg>
				BrisOPT
			</div>
		</div>
	);
}
