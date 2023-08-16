'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import * as z from 'zod';

import { Button } from '@/components/ui/button';
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormMessage
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';

const formSchema = z.object({
	email: z.string().email({
		message: 'Please provide a valid email.'
	})
});

const LoginForm = () => {
	const [isLoading, setIsLoading] = useState(false);
	const { push } = useRouter();
	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema)
	});

	function onSubmit(values: z.infer<typeof formSchema>) {
		setIsLoading(true);
		console.log(values)

		// Stubbing login logic
		setTimeout(() => {
			push('/dashboard');
		}, 2000);
	}

	return (
		<Form {...form}>
			<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
				<FormField
					control={form.control}
					name="email"
					render={({ field }) => (
						<FormItem>
							<FormControl>
								<Input
									type="email"
									placeholder="joe@shmoe.com"
									autoCapitalize="none"
									autoComplete="email"
									autoCorrect="off"
									disabled={isLoading}
									{...field}
								/>
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>
				<Button type="submit" className="w-full" disabled={isLoading}>
					{isLoading ? (
						<Loader2 className="animate-spin" size={16} />
					) : (
						'continue'
					)}
				</Button>
			</form>
		</Form>
	);
};
export default LoginForm;